import unittest

def run_all_tests():
    """
    Lädt und führt alle Unittests des Projekts aus.
    """
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir=".", pattern="test_*.py")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    run_all_tests()