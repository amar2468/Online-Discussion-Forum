import unittest
import requests

class unit_test_forum(unittest.TestCase):

    def test_forum_topics(self):
        response = requests.get("http://studentdiscussiontest-env.eba-ycpiemz9.us-east-1.elasticbeanstalk.com/visit_subforum/Computer%20Science")

        # Verify that the response contains the expected data
        self.assertEqual(response.status_code, 200)
        print("success!")
unit_test_forum()