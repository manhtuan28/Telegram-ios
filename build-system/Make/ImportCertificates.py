import os
import sys
import argparse

from BuildEnvironment import run_executable_with_output

def import_certificates(certificatesPath):
    if not os.path.exists(certificatesPath):
        print('{} does not exist'.format(certificatesPath))
        sys.exit(1)

    keychain_dir = os.path.expanduser("~/Library/Keychains")
    os.makedirs(keychain_dir, exist_ok=True)
    keychain_name = os.path.join(keychain_dir, "temp.keychain-db")
    keychain_password = "secret"

    try:
        run_executable_with_output("security", arguments=["delete-keychain", keychain_name])
    except Exception:
        pass

    run_executable_with_output("security", arguments=[
        "create-keychain",
        "-p",
        keychain_password,
        keychain_name
    ], check_result=True)

    run_executable_with_output("security", arguments=["set-keychain-settings", "-lut", "7200", keychain_name])
    run_executable_with_output("security", arguments=["unlock-keychain", "-p", keychain_password, keychain_name])

    try:
        raw_keychains = run_executable_with_output("security", arguments=["list-keychains", "-d", "user"])
        keychain_list = [kc.strip().strip('"') for kc in raw_keychains.splitlines() if kc.strip()]
    except Exception:
        keychain_list = []

    if keychain_name not in keychain_list:
        keychain_list.insert(0, keychain_name)

    run_executable_with_output("security", arguments=["list-keychains", "-d", "user", "-s"] + keychain_list, check_result=True)
    run_executable_with_output("security", arguments=["default-keychain", "-d", "user", "-s", keychain_name], check_result=False)

    for file_name in sorted(os.listdir(certificatesPath)):
        file_path = os.path.join(certificatesPath, file_name)
        if file_path.endswith(".p12") or file_path.endswith(".cer"):
            print(f"Importing {file_path} into {keychain_name}...")
            try:
                run_executable_with_output("security", arguments=[
                    "import",
                    file_path,
                    "-k",
                    keychain_name,
                    "-P",
                    "",
                    "-A",
                    "-T", "/usr/bin/codesign",
                    "-T", "/usr/bin/security"
                ], check_result=False)
            except Exception as e:
                print(f"Notice when importing {file_path}: {e}")

    if os.path.exists("build-system/AppleWWDRCAG3.cer"):
        try:
            run_executable_with_output("security", arguments=[
                "import",
                "build-system/AppleWWDRCAG3.cer",
                "-k",
                keychain_name,
                "-P",
                "",
                "-A",
                "-T", "/usr/bin/codesign",
                "-T", "/usr/bin/security"
            ], check_result=False)
        except Exception as e:
            print(f"Notice when importing AppleWWDRCAG3.cer: {e}")

    run_executable_with_output("security", arguments=[
        "set-key-partition-list",
        "-S",
        "apple-tool:,apple:,codesign:",
        "-s",
        "-k",
        keychain_password,
        keychain_name
    ], check_result=False)

    run_executable_with_output("security", arguments=["unlock-keychain", "-p", keychain_password, keychain_name])
    
    try:
        identities = run_executable_with_output("security", arguments=["find-identity", "-v", "-p", "codesigning"])
        print("Available signing identities:\n", identities)
    except Exception as e:
        print("Could not list identities:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="build")

    parser.add_argument(
        "--path",
        required=True,
        help="Path to certificates."
    )

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    import_certificates(args.path)
