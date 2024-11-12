#!/usr/bin/env python3
import argparse
import getpass
import sys

from pyicloud import PyiCloudService
import click


def check_two_factor(api: PyiCloudService) -> bool:
    if api.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            return False

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)

            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

    elif api.requires_2sa:
        print("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print(
                "  %s: %s" % (i, device.get('deviceName',
                                            "SMS to %s" % device.get('phoneNumber')))
            )

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            return False

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            return False

    # got here, it's good for now
    return True


if __name__ == "__main__":
    """
    Stub script entry point. Authenticates iCloud SDK, and gathers options from command line to run
    :return: No return
    """

    # Parse arguments
    parser = argparse.ArgumentParser(description="Find / Delete files from iCloud Drive that are too long.")

    # support for china stuff if it ever exists
    # api_group = parser.add_argument_group('API',
    #                                       'These options change how this program connects to the API.')
    # api_group.add_argument("--china-mainland", "-C",
    #                        help="Flag to specify mainland China account/APIs.",
    #                        action='store_true',
    #                        default=False)

    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email instead of prompting.",
                             default=None)
    auth_group = parser.add_mutually_exclusive_group()

    auth_group.add_argument("--password", "-PW",
                            help="(NOT RECOMMENDED) Use this Password instead prompting",
                            default=None)
    auth_group.add_argument("--keychain", "-K", help="Use system keychain for password authentication.",
                            action='store_true',
                            default=False)
    # login_group.add_argument("--insecure", "-I", help="Do not verify SSL certificate",
    #                          action='store_true',
    #                          default=False)

    ARGS = vars(parser.parse_args())

    if ARGS["email"]:
        user_email = ARGS["email"]
    else:
        user_email = input(f"iCloud login: ")

    # figure out password
    if ARGS["keychain"] is False:
        if ARGS["password"]:
            user_password = ARGS["password"]
        else:
            user_password = getpass.getpass(f"Password for {user_email}: ")

        api = PyiCloudService(user_email, user_password)
    else:
        api = PyiCloudService(user_email)

    if not check_two_factor(api):
        sys.exit("Two-factor authentication failure.")

    print(api.drive.dir())

    breakpoint()






