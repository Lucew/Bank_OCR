import re
import json
from termcolor import colored


def load_tests(path='00-Intro.tex') -> list[list]:

    # make the regular expression
    use_case_expression = re.compile(r"[\s_|\n]{1,27}\n[\s_|]{27}\n[\s_|]{27}\n\n=>\s[0-9?]{9}[^\n]*\n")

    # load the document
    with open(path, 'r', encoding="utf8") as f:
        text = f.read()

    # find all the test cases
    tests = re.findall(use_case_expression, text)

    # split representation and result
    tests = [t.split('=> ') for t in tests]

    # go through all tests and fix some formatting
    for counter, test in enumerate(tests):

        # correct the errors
        tests[counter][0] = test[0][:-2].replace('\n\n\n', '\n\n').replace('\n\n', ' '*27 + '\n')

        if test[1][-2] == " ":
            tests[counter][1] = test[1][:-2]
        else:
            tests[counter][1] = test[1][:-1]

    return tests


def create_dict_string(test_cases: list = None) -> dict:

    # get the test cases if not given
    if test_cases is None:
        test_cases = load_tests()

    # get the string representation of the numbers 1-9
    numbers = separate_numbers(test_cases[10][0])

    # get the string representation of the number 0
    zero_numbers = separate_numbers(test_cases[0][0])

    # append the zero to the numbers 1-9
    numbers.insert(0, zero_numbers[0])

    # get the key values in the right formatting
    key_value_string = [repr(number) + ":" + str(counter) for counter, number in enumerate(numbers)]
    key_value_string = [stringi.replace("'", '"') for stringi in key_value_string]

    # make the json conforming string
    dict_string = f'{{{",".join(key_value_string)}}}'

    number_dict = json.loads(dict_string)

    return number_dict


def separate_numbers(representation: str) -> list[str]:

    # separate the numbers in the string representation
    numbers = ['' for _ in range(9)]
    for counter in range(9):
        for line in range(3):
            numbers[counter] += representation[line*28+counter*3:line*28 + counter*3 + 3] + '\n'

    return numbers


def translate_number(case: str, number_dict: dict = None) -> str:

    # get the dict if it is none
    if number_dict is None:
        number_dict = create_dict_string()

    # separate the numbers
    numbers = separate_numbers(case)

    # translate the numbers using the dict
    result = ''
    for number in numbers:
        result += str(number_dict.get(number, '?'))

    return result


def validate_with_checksum(numbers: str) -> str:

    # create the result
    result = ' ILL'

    # go through the numbers and calculate checksum
    checksum = 0
    for counter, number in enumerate(numbers[::-1]):

        # check if we have question marks
        if number == '?':
            return result
        checksum += (counter+1)*int(number)

    # check the checksum
    result = "" if checksum % 11 == 0 else " ERR"

    return result


def attempt_correction(numbers: list[str], result: str, number_dict: dict = None) -> list[str]:

    # get the dict if it is none
    if number_dict is None:
        number_dict = create_dict_string()

    # go through all separate numbers
    alternatives = []
    for num_counter, number in enumerate(numbers):
        for char_counter, character in enumerate(number):
            # check whether it is empty
            if character == " ":

                # get the replacement character (line if outside, underscore if inside)
                replacement = "|" if char_counter % 2 == 0 else "_"

            elif character == "_" or character == "|":
                # replace underscore or bars with empty character
                replacement = " "

            else:
                continue

            # get the new number
            new_number = number[:char_counter] + replacement + number[char_counter+1:]  # build string representation
            new_number = number_dict.get(new_number, '?')  # get the new number

            # reconstruct the complete number (using surrounding numbers)
            new_number = result[:num_counter] + str(new_number) + result[num_counter + 1:]

            # check the new number
            if validate_with_checksum(new_number) == "":
                alternatives.append(new_number)
    # sort the alternatives
    if len(alternatives) > 1:
        alternatives = sorted(alternatives, key=lambda x: int(x))
    return alternatives


def test_case1(test_cases: list = None):

    # load test cases if not given
    if test_cases is None:
        test_cases = load_tests()

    print('\n-----------------')
    print('|  Test Case 1  |')
    print('-----------------')

    # go through all tests
    for test in test_cases[:11]:

        # get the result
        result = translate_number(test[0])

        # compare the result with the right output and write message
        print()
        print(colored(test[0], 'green' if result == test[1] else 'red'))
        print(colored(f'Translation: [{result}], Correct: [{test[1]}].', 'green' if result == test[1] else 'red'))


def test_case2():

    # test cases from the file
    test_cases = [("457508000", ""), ("664371495", " ERR"), ("86110??36",  " ILL")]

    print('\n-----------------')
    print('|  Test Case 2  |')
    print('-----------------')

    # go through the test
    for test in test_cases:
        # get the output of the checksum function
        result = validate_with_checksum(test[0])

        # print an output
        print()
        print(colored(test[0], 'green' if result == test[1] else 'red'))
        print(colored(f'Result: [{result}], Correct: [{test[1]}].', 'green' if result == test[1] else 'red'))


def test_case3(test_cases: list = None):
    # load test cases if not given
    if test_cases is None:
        test_cases = load_tests()

    print('\n-----------------')
    print('|  Test Case 3  |')
    print('-----------------')

    # go through all tests (start at test 15)
    for test in test_cases[11:14]:

        # get the result for one number
        result = translate_number(test[0])

        # check whether they are valid
        check_result = validate_with_checksum(result)

        # add the check to the result
        result += check_result

        # compare the result with the right output and write message
        print()
        print(colored(test[0], 'green' if result == test[1] else 'red'))
        print(colored(f'Translation: [{result}], Correct: [{test[1]}].', 'green' if result == test[1] else 'red'))


def test_case4(test_cases: list = None):
    # load test cases if not given
    if test_cases is None:
        test_cases = load_tests()

    print('\n-----------------')
    print('|  Test Case 4  |')
    print('-----------------')

    # go through all tests (start at test 15)
    for test in test_cases[14:]:

        # get the result for one number
        result = translate_number(test[0])

        # check whether they are valid
        check_result = validate_with_checksum(result)

        # attempt correction if check result is bad
        if check_result == ' ILL' or check_result == ' ERR':
            alternatives = attempt_correction(separate_numbers(test[0]), result)

            # do something about alternatives
            if len(alternatives) == 1:
                result = alternatives[0]
            elif len(alternatives) > 1:
                result = result + ' AMB ' + "[" + ", ".join([repr(alternative) for alternative in alternatives]) + "]"

        # compare the result with the right output and write message
        print()
        print(colored(test[0], 'green' if result == test[1] else 'red'))
        print(colored(f'Translation: [{result}], Correct: [{test[1]}].', 'green' if result == test[1] else 'red'))


if __name__ == '__main__':
    test_case1()
    test_case2()
    test_case3()
    test_case4()
