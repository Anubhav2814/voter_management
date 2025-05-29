#!/usr/bin/env python
import os
import sys
from notifications.test_sms import test_sms_sending, test_with_real_voter

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.append(os.getcwd())

    # Run the test module
    from notifications.test_sms import test_sms_sending, test_with_real_voter

    print("Running SMS tests...")
    test_sms_sending()
    test_with_real_voter()