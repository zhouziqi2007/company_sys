import unittest

from app.subscription import build_subscription_reply


class SubscriptionReplyTests(unittest.TestCase):
    def test_subscribe_message_in_chinese(self):
        intent, reply = build_subscription_reply("你好，我想订阅")
        self.assertEqual(intent, "subscribe")
        self.assertIn("邮箱地址", reply)

    def test_unknown_message(self):
        intent, _ = build_subscription_reply("你好")
        self.assertEqual(intent, "unknown")


if __name__ == "__main__":
    unittest.main()
