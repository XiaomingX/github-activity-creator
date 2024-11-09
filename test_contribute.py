#!/usr/bin/env python3
import unittest
import contribute
from subprocess import check_output

class TestContribute(unittest.TestCase):
    """测试GitHub贡献相关功能的测试类"""
    
    def setUp(self):
        """测试前的初始化设置"""
        self.default_args = ['-nw']
        self.test_num = 11  # 仅用于单元测试的固定值
        
    def test_arguments(self):
        """测试参数解析功能"""
        args = self._get_parsed_args()
        self._verify_default_args(args)
        
    def test_contributions_per_day(self):
        """测试每日贡献次数计算"""
        args = self._get_parsed_args()
        daily_contributions = contribute.contributions_per_day(args)
        self._verify_contribution_range(daily_contributions)
        
    def test_commits(self):
        """测试提交功能"""
        contribute.NUM = self.test_num
        test_args = self._get_test_commit_args()
        contribute.main(test_args)
        commit_count = self._get_commit_count()
        self._verify_commit_count(commit_count)
        
    def _get_parsed_args(self):
        """获取解析后的参数"""
        return contribute.arguments(self.default_args)
    
    def _verify_default_args(self, args):
        """验证默认参数设置"""
        self.assertTrue(args.no_weekends)
        self.assertEqual(args.max_commits, 10)
        self.assertTrue(1 <= contribute.contributions_per_day(args) <= 20)
        
    def _verify_contribution_range(self, count):
        """验证贡献次数是否在有效范围内"""
        self.assertTrue(1 <= count <= 20)
        
    def _get_test_commit_args(self):
        """获取测试提交所需的参数"""
        return [
            '-nw',
            '--user_name=sampleusername',
            '--user_email=your-username@users.noreply.github.com',
            '-mc=12',
            '-fr=82',
            '-db=10',
            '-da=15'
        ]
        
    def _get_commit_count(self):
        """获取Git提交计数"""
        return int(check_output(['git', 'rev-list', '--count', 'HEAD']).decode('utf-8'))
        
    def _verify_commit_count(self, count):
        """验证提交次数是否在预期范围内"""
        self.assertTrue(1 <= count <= 20 * (10 + 15))

def main():
    """主函数"""
    unittest.main()

if __name__ == '__main__':
    main()