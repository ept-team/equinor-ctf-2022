
import json

def main():

    with open("pincode_data.json") as f:
        data = json.load(f)

    print("Please provide pincodes:")
    print("Format is without spaces - i.e if the pincode is: 15 10 4 3 2 please input 1510432")
    pincode_1 = input(">").strip()
    pincode_2 = input(">").strip()

    secrets = data.get(pincode_1+pincode_2, None)

    if secrets:
        print(f"The secret for this combination is: {secrets}")
    else:
        print("Sorry, the pincodes you provided are not correct")


if __name__ == "__main__":
    main()
