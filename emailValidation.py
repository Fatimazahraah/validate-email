from validate_email_address import validate_email
import csv
import time
import threading
import concurrent.futures

def get_emails(file_path):
    """ gets the list of emails from the csv file """
    emails = []
    with open(file_path, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            emails.append(row.get('email'))
    return emails

def check_emails(emails):
    result = []

    def temp(_email):
        def check_is_valid():
            return validate_email(_email, check_mx=True)

        def check_is_exist():
            return validate_email(_email, verify=True)
        """ execution in parallel for checking both of validity and existence """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            is_valid = executor.submit(check_is_valid)
            is_exist = executor.submit(check_is_exist)
            is_valid_results = is_valid.result()
            is_exist_results = is_exist.result()
        print(is_valid_results)
        print(is_exist_results)
        result.append(
            {
                "email": _email,
                "is_valid": is_valid_results if isinstance(is_valid_results, bool) else "Not mentioned",
                "is_exist": is_exist_results if isinstance(is_exist_results, bool) else "Not mentioned"
            }
        )

    """ the case using threading : execution in parallel for the given emails """
    start_time = time.time()
    thread_list = []
    for email in emails:
        t = threading.Thread(target=temp, args=(email,))
        thread_list.append(t)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    print("total", time.time() - start_time)
    return result


def export_results(result):
    header = result[0].keys()
    with open('results.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, header)
        dict_writer.writeheader()
        dict_writer.writerows(result)


export_results(check_emails(get_emails("save_location")))
