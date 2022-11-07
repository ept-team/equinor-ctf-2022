const BASE: &str = "http://io3.ept.gg:32350";

use colored::Colorize;
use rand::Rng;
use serde::Deserialize;
use std::{
    collections::{HashMap, HashSet},
    fs::File,
    io::{BufRead, BufReader, Read, Write},
    iter::zip,
    path::Path,
    time::Instant,
};

#[derive(Debug, Deserialize)]
struct Session {
    token: String,
}

#[derive(Clone, Copy, Debug, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Color {
    Green,
    Yellow,
    #[serde(rename = "none")]
    Black,
}

#[derive(Debug, Deserialize)]
struct Character {
    char: char,
    hint: Color,
}

#[derive(Debug, Deserialize)]
struct GuessResponse {
    hash: Vec<Character>,
    level: usize,
    //attempt: usize,
    max_attempts: usize,
    flag: String,
}

impl GuessResponse {
    fn text(&self) -> String {
        self.hash.iter().map(|ch| ch.char).collect()
    }

    fn hints(&self) -> Vec<Color> {
        self.hash.iter().map(|ch| ch.hint).collect()
    }
}

impl Session {
    fn guess_request(&self, password: &str) -> Result<GuessResponse, ureq::Error> {
        let mut guess_url = String::from(BASE);
        guess_url.push_str("/api/guess");

        //let res = ureq::post(&guess_url).send_json(ureq::json!(
        //{
        //    "token": self.token,
        //    "password": password
        //}
        //)).unwrap();
        //println!("{}", res.into_string().unwrap());

        let req = ureq::post(&guess_url).send_json(ureq::json!(
        {
            "token": self.token,
            "password": password
        }
        ));

        match req {
            Err(ureq::Error::Status(_code, response)) => {
                panic!("{:?}", response.into_string().unwrap());
            }
            _ => {}
        }

        let req = req.unwrap();
        let req = req.into_string().unwrap();

        let json: Result<GuessResponse, _> = serde_json::from_str(&req);

        if let Ok(json) = json {
            Ok(json)
        } else {
            panic!("{}", req);
        }
    }
}

fn get_token() -> Result<Session, ureq::Error> {
    let mut req_url = String::from(BASE);
    req_url.push_str("/api/session");

    Ok(ureq::get(&req_url).call()?.into_json()?)
}

struct Possible {
    contents: Vec<HashSet<u8>>,
}

impl Possible {
    fn new(size: usize) -> Self {
        let mut full_set = HashSet::new();
        for v in b"0123456789abcdef" {
            full_set.insert(*v);
        }

        Possible {
            contents: (0..size).map(|_| full_set.clone()).collect(),
        }
    }
}

fn remove_impossible_hashes(
    remaining_hashes: &[Vec<u8>],
    yellows: &HashMap<u8, usize>,
    size: usize,
) -> Vec<Vec<u8>> {
    remaining_hashes
        .iter()
        .filter_map(|h| {
            for (key, val) in yellows.iter() {
                let occurances = h[..size].iter().filter(|char| *char == key).count();

                if occurances != *val {
                    return None;
                }
            }

            Some(h.clone())
        })
        .collect()
}

fn generate_guess(hashes: &[Vec<u8>], its: usize, size: usize) -> String {
    fn compare(guess: &Vec<u8>, hash: &[u8]) -> [u8; 32] {
        let mut out = [0; 32];
        for i in 0..guess.len() {
            let n = if hash[i] == guess[i] {
                0
            } else if hash.contains(&guess[i]) {
                1
            } else {
                2
            };
            out[i] = n;
        }
        out
    }

    fn find_num_uniq(hashes: &[Vec<u8>], guess: &Vec<u8>) -> usize {
        let mut uniq = HashSet::new();
        for h in hashes {
            uniq.insert(compare(guess, h));
        }
        uniq.len()
    }

    let mut best = 0;
    let mut best_guess = String::new();
    for _ in 0..its {
        let guess = rand::thread_rng()
            .sample_iter(&rand::distributions::Alphanumeric)
            .take(32)
            .map(char::from)
            .collect();

        let digest = md5::compute(&guess);
        let hex = format!("{:x}", digest);
        let hex = &hex[..size];

        let score = find_num_uniq(hashes, &hex.as_bytes().to_vec());
        if score > best {
            best = score;
            best_guess = guess;
            if score == hashes.len() {
                let perfect = "perfect".cyan();
                println!("Found a {perfect} hash, {}/{}", score, hashes.len());
                break; // early exit, found a perfect hash
            }
        }
    }

    best_guess
}

fn colored_response(resp: &GuessResponse) {
    print!("< ");
    for ch in &resp.hash {
        let mut txt = String::new();
        txt.push(ch.char);

        let txt = match ch.hint {
            Color::Green => txt.green(),
            Color::Yellow => txt.yellow(),
            Color::Black => txt.red(),
        };

        print!("{}", txt);
    }
    println!();
}

fn interact(
    wordlist: &Wordlist,
    session: &Session,
    mut tries: usize,
) -> Result<Vec<Vec<u8>>, ureq::Error> {
    // pre-generated pretty optimal string
    let mut password = String::from("bdpbyjtjabkxabpcdrkjeyasuwicjyoy");

    let mut yellows = HashMap::new();

    let mut remaining_hashes = wordlist.hashes.clone();

    loop {
        println!("> {}", password);
        let resp = session.guess_request(&password)?;
        colored_response(&resp);

        let mut possible = Possible::new(resp.hints().len());

        for i in 0..resp.hints().len() {
            let text = resp.text();
            let bytes = text.as_bytes();

            match resp.hints()[i] {
                Color::Green => {
                    possible.contents[i].clear();
                    possible.contents[i].insert(bytes[i]);
                }
                Color::Yellow => {
                    possible.contents[i].remove(&bytes[i]);
                }
                Color::Black => {
                    let mut yellow_cnt = 0;

                    for j in 0..resp.hints().len() {
                        if matches!(resp.hints()[j], Color::Yellow | Color::Green)
                            && bytes[j] == bytes[i]
                        {
                            yellow_cnt += 1
                        }
                    }

                    if yellows.contains_key(&bytes[i]) {
                        assert_eq!(yellows[&bytes[i]], yellow_cnt);
                    }

                    yellows.insert(bytes[i], yellow_cnt);
                }
            }
        }

        let yellow_before = remaining_hashes.len();
        remaining_hashes =
            remove_impossible_hashes(&remaining_hashes, &yellows, possible.contents.len());
        println!("YELLOW {} -> {}", yellow_before, remaining_hashes.len());

        if remaining_hashes.len() < tries {
            return Ok(remaining_hashes);
        }

        let hashes = find_hash(possible, &remaining_hashes);
        println!("NORMAL {} -> {}", remaining_hashes.len(), hashes.len());
        remaining_hashes = hashes;

        if remaining_hashes.len() < tries {
            return Ok(remaining_hashes);
        }

        tries -= 1;

        // 50 when we're at max, but possibly million+ when only a few
        // we can afford to run more when we have less elements
        //let iters = max_runtime / real_size;
        let iters = 15_000_000 / remaining_hashes.len();

        let subset = &remaining_hashes[..];

        println!("Generate guess...");
        password = generate_guess(subset, iters, resp.hash.len());
    }
}

fn find_hash(possible: Possible, remaining_hashes: &[Vec<u8>]) -> Vec<Vec<u8>> {
    remaining_hashes
        .iter()
        .filter_map(|hash| {
            for (char, pos) in zip(hash.iter(), possible.contents.iter()) {
                if !pos.contains(char) {
                    return None;
                }
            }
            Some(hash.clone())
        })
        .collect()
}

#[derive(rkyv::Archive, rkyv::Deserialize, rkyv::Serialize, bytecheck::CheckBytes)]
struct Wordlist {
    words: Vec<Vec<u8>>,
    hashes: Vec<Vec<u8>>,
}

fn read_rockyou() -> Wordlist {
    if Path::new("cache").exists() {
        println!("reading...");
        let mut cache = File::open("cache").unwrap();
        let mut buf = Vec::new();
        cache.read_to_end(&mut buf).unwrap();

        return unsafe { rkyv::from_bytes_unchecked(&buf).unwrap() };
    }

    let instant = Instant::now();

    let file = File::open("../rockyou.txt").unwrap();
    let mut file = BufReader::new(file);

    let mut words = Vec::new();
    let mut hashes = Vec::new();

    let mut i = 0;
    let mut buf = Vec::new();
    while file.read_until(b'\n', &mut buf).is_ok() {
        if buf.is_empty() {
            break;
        }
        i += 1;
        if i % 500_000 == 0 {
            println!("{}", i);
        }

        let password = &buf[..buf.len() - 1];

        let digest = md5::compute(password);
        let hex = format!("{:x}", digest);

        words.push(password.to_vec());
        hashes.push(hex.into_bytes());

        buf.clear();
    }
    println!("{} lines", i);

    let elapsed = instant.elapsed();
    println!("read in {:?}", elapsed);

    let wl = Wordlist { words, hashes };

    let bytes = rkyv::to_bytes::<_, 0>(&wl).unwrap();
    let mut cache = File::create("cache").unwrap();
    println!("read");
    cache.write_all(&bytes).unwrap();

    wl
}

fn password_from_hash(wordlist: &Wordlist, target: &[u8]) -> String {
    for (hash, pass) in zip(wordlist.hashes.iter(), wordlist.words.iter()) {
        if hash == target {
            return String::from_utf8(pass.to_vec()).unwrap();
        }
    }
    panic!()
}

fn main() {
    let wordlist = read_rockyou();
    println!("read");

    let mut req_url = String::from(BASE);
    req_url.push_str("/api/session");

    let session = get_token().unwrap();

    let mut tries = 0;
    let mut level = 1;

    loop {
        let hashes = interact(&wordlist, &session, tries).unwrap();

        println!(
            "{}",
            format!("Trying to submit {} flags", hashes.len()).green()
        );

        for h in hashes {
            let p = password_from_hash(&wordlist, &h);
            let r = session.guess_request(&p).unwrap();

            if r.flag.contains("EPT{") {
                println!("{}", r.flag.bold());
                return;
            }

            if r.level > level {
                level = r.level;
                tries = r.max_attempts;
                println!();
                println!("{}", format!("== LEVEL {} ==", level).purple());
                break;
            }
        }
    }
}
