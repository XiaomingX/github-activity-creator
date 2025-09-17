#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
from datetime import datetime, timedelta
from random import randint
import unittest
from unittest.mock import patch, Mock
from subprocess import CalledProcessError, check_output


def main(default_args=None):
    """主函数：解析参数并执行提交生成流程"""
    # 处理默认参数
    args = parse_arguments(default_args or sys.argv[1:])
    today = datetime.now()

    # 确定仓库目录名称
    repo_dir = determine_repo_directory(args.repository, today)
    
    # 创建并进入仓库目录
    setup_repo_directory(repo_dir, args.force)
    os.chdir(repo_dir)
    print(f"进入工作目录: {os.getcwd()}")

    # 初始化Git仓库并配置用户信息
    init_git_repo()
    configure_git_user(args.user_name, args.user_email)

    # 计算提交日期范围
    start_date, end_date = calculate_date_range(args, today)
    total_days = (end_date - start_date).days + 1
    print(f"将在 {total_days} 天内生成提交记录，范围: "
          f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")

    # 生成提交记录
    generate_commits(args, start_date, end_date)

    # 推送到远程仓库（如果指定）
    if args.repository:
        push_to_remote(args.repository)

    print("\n✅ 仓库生成完成！")


def determine_repo_directory(repo_url, current_date):
    """确定仓库目录名称"""
    if repo_url:
        # 从URL中提取仓库名（去掉.git后缀）
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        return repo_name.strip()
    # 使用当前时间作为目录名
    return f"repo-{current_date.strftime('%Y%m%d-%H%M%S')}"


def setup_repo_directory(repo_dir, force):
    """创建仓库目录，支持强制覆盖"""
    if os.path.exists(repo_dir):
        if not force:
            sys.exit(f"错误: 目录 '{repo_dir}' 已存在，请删除后重试或使用 --force 强制覆盖")
        # 强制删除现有目录
        import shutil
        shutil.rmtree(repo_dir)
        print(f"已删除现有目录: {repo_dir}")
    
    os.mkdir(repo_dir)
    print(f"创建仓库目录: {repo_dir}")


def init_git_repo():
    """初始化Git仓库"""
    run_command(['git', 'init', '-b', 'main'], "初始化Git仓库")


def configure_git_user(user_name, user_email):
    """配置Git用户信息"""
    if user_name:
        run_command(['git', 'config', 'user.name', user_name], "配置用户名")
    if user_email:
        run_command(['git', 'config', 'user.email', user_email], "配置用户邮箱")


def calculate_date_range(args, today):
    """计算提交的日期范围"""
    # 如果指定了具体开始日期，则优先使用
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        start_date = today - timedelta(days=args.days_before)
    
    # 如果指定了具体结束日期，则优先使用
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    else:
        end_date = today + timedelta(days=args.days_after)
    
    # 确保开始日期不晚于结束日期
    if start_date > end_date:
        start_date, end_date = end_date, start_date
        
    return start_date, end_date


def generate_commits(args, start_date, end_date):
    """生成指定日期范围内的提交记录"""
    current_day = start_date
    while current_day <= end_date:
        # 跳过周末（如果启用）
        if args.no_weekends and current_day.weekday() >= 5:
            current_day += timedelta(days=1)
            continue
            
        # 根据频率决定当天是否生成提交
        if randint(0, 100) < args.frequency:
            commit_count = randint(1, args.max_commits)
            print(f"在 {current_day.strftime('%Y-%m-%d')} 生成 {commit_count} 次提交")
            
            # 生成多次提交
            for minute_offset in range(commit_count):
                commit_time = current_day.replace(
                    hour=args.commit_hour, 
                    minute=args.commit_minute
                ) + timedelta(minutes=args.commit_interval * minute_offset)
                
                # 确保提交时间在当天（防止跨天）
                if commit_time.date() != current_day.date():
                    break
                    
                create_commit(commit_time, args.commit_files, args.message_template)
        
        current_day += timedelta(days=1)


def create_commit(commit_time, file_paths, msg_template):
    """创建一个带有指定时间的提交"""
    # 生成提交消息
    commit_msg = msg_template.format(
        date=commit_time.strftime('%Y-%m-%d'),
        time=commit_time.strftime('%H:%M:%S')
    )
    
    # 写入文件内容（支持多个文件）
    for file_path in file_paths:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入随机内容，增加多样性
        with open(file_path, 'a', encoding='utf-8') as f:
            content = f"Updated at {commit_time.strftime('%Y-%m-%d %H:%M:%S')} - {randint(1000, 9999)}\n"
            f.write(content)
        
        run_command(['git', 'add', file_path], f"暂存文件: {file_path}")
    
    # 执行Git提交
    run_command([
        'git', 'commit', 
        '-m', commit_msg, 
        '--date', commit_time.strftime('%Y-%m-%d %H:%M:%S')
    ], f"创建提交: {commit_msg[:30]}...")


def push_to_remote(repo_url):
    """推送到远程仓库"""
    run_command(['git', 'remote', 'add', 'origin', repo_url], 
                "添加远程仓库", ignore_error=True)
    run_command(['git', 'remote', 'set-url', 'origin', repo_url], 
                "更新远程仓库地址", ignore_error=True)
    run_command(['git', 'branch', '-M', 'main'], "重命名主分支", ignore_error=True)
    run_command(['git', 'push', '-u', 'origin', 'main'], "推送到远程仓库")


def run_command(command, description, ignore_error=False):
    """执行命令并检查结果"""
    try:
        result = subprocess.run(
            command,
            check=not ignore_error,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return True
        if not ignore_error:
            print(f"⚠️ 命令执行失败 ({description}): {result.stderr}", file=sys.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行出错 ({description}): {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ 未找到命令: {command[0]}，请确保已安装相关工具", file=sys.stderr)
        sys.exit(1)
    return False


def parse_arguments(args):
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="自动生成Git提交记录工具")
    
    # 目录处理选项
    parser.add_argument('-f', '--force', action='store_true',
                        help="强制覆盖已存在的仓库目录")
    
    # 提交时间配置
    parser.add_argument('-nw', '--no_weekends', action='store_true',
                        help="不在周末生成提交")
    parser.add_argument('-ch', '--commit_hour', type=int, default=20,
                        choices=range(0, 24),
                        help="每天提交的小时数 (0-23)，默认20点")
    parser.add_argument('-cm', '--commit_minute', type=int, default=0,
                        choices=range(0, 60),
                        help="每天首次提交的分钟数 (0-59)，默认0分")
    parser.add_argument('-ci', '--commit_interval', type=int, default=30,
                        help="同天内提交的时间间隔（分钟），默认30分钟")
    
    # 提交数量配置
    parser.add_argument('-mc', '--max_commits', type=int, default=10,
                        choices=range(1, 21),  # 限制1-20的范围
                        help="每天最大提交次数 (1-20)，默认10")
    parser.add_argument('-fr', '--frequency', type=int, default=80,
                        choices=range(0, 101),  # 限制0-100的范围
                        help="提交概率 (0-100%%)，默认80%%")
    
    # 仓库配置
    parser.add_argument('-r', '--repository',
                        help="远程仓库URL (例如: git@github.com:user/repo.git)")
    parser.add_argument('-un', '--user_name',
                        help="Git用户名（覆盖全局配置）")
    parser.add_argument('-ue', '--user_email',
                        help="Git用户邮箱（覆盖全局配置）")
    
    # 日期范围配置（支持两种方式：相对天数和绝对日期）
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('-db', '--days_before', type=int, default=365,
                           help="从多少天前开始生成提交，默认365天")
    date_group.add_argument('-sd', '--start_date',
                           help="开始日期（格式: YYYY-MM-DD），与--days_before互斥")
    
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('-da', '--days_after', type=int, default=0,
                           help="生成未来多少天的提交，默认0天")
    date_group.add_argument('-ed', '--end_date',
                           help="结束日期（格式: YYYY-MM-DD），与--days_after互斥")
    
    # 自定义内容配置
    parser.add_argument('-cf', '--commit_files', nargs='+', default=['README.md'],
                        help="提交的文件列表，默认: README.md")
    parser.add_argument('-mt', '--message_template', 
                        default="Contribution on {date} {time}",
                        help="提交消息模板，可用变量: {date}, {time}")
    
    return parser.parse_args(args)


class TestGitCommitGenerator(unittest.TestCase):
    """测试Git提交记录生成工具的测试类"""
    
    def setUp(self):
        """测试前的初始化设置"""
        self.default_args = ['-nw']  # 默认不包含周末
        self.test_num = 11  # 测试用固定值
        self.expected_min_commits = 1
        self.expected_max_commits = 20
    
    def test_default_arguments_parsing(self):
        """测试默认参数解析是否正确"""
        args = parse_arguments(self.default_args)
        
        self.assertTrue(args.no_weekends, "默认应不包含周末")
        self.assertEqual(args.max_commits, 10, "默认最大提交数应为10")
        self.assertEqual(args.frequency, 80, "默认提交频率应为80%")
        self.assertEqual(args.commit_files, ['README.md'], "默认提交文件应为README.md")
    
    def test_date_range_calculation(self):
        """测试日期范围计算逻辑"""
        today = datetime.now()
        
        # 测试相对日期
        args = parse_arguments(['-db=10', '-da=5'])
        start, end = calculate_date_range(args, today)
        self.assertEqual((today - start).days, 10)
        self.assertEqual((end - today).days, 5)
        
        # 测试绝对日期
        args = parse_arguments(['-sd=2023-01-01', '-ed=2023-01-10'])
        start, end = calculate_date_range(args, today)
        self.assertEqual(start.strftime('%Y-%m-%d'), '2023-01-01')
        self.assertEqual(end.strftime('%Y-%m-%d'), '2023-01-10')
        
        # 测试日期交换（开始日期晚于结束日期）
        args = parse_arguments(['-sd=2023-01-10', '-ed=2023-01-01'])
        start, end = calculate_date_range(args, today)
        self.assertEqual(start.strftime('%Y-%m-%d'), '2023-01-01')
        self.assertEqual(end.strftime('%Y-%m-%d'), '2023-01-10')
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        """测试命令执行成功的情况"""
        mock_run.return_value = Mock(returncode=0, stderr='')
        result = run_command(['echo', 'test'], "测试命令")
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """测试命令执行失败的情况"""
        mock_run.return_value = Mock(returncode=1, stderr='error message')
        
        with self.assertRaises(SystemExit):
            run_command(['false'], "测试失败命令")
    
    @patch('os.mkdir')
    @patch('os.path.exists')
    def test_setup_repo_directory(self, mock_exists, mock_mkdir):
        """测试仓库目录设置逻辑"""
        # 测试新目录创建
        mock_exists.return_value = False
        setup_repo_directory('test-repo', False)
        mock_mkdir.assert_called_once_with('test-repo')
        
        # 测试目录已存在但不强制覆盖
        mock_exists.return_value = True
        with self.assertRaises(SystemExit):
            setup_repo_directory('test-repo', False)
    
    def test_commit_message_template(self):
        """测试提交消息模板渲染"""
        test_time = datetime(2023, 1, 1, 12, 34, 56)
        template = "Test commit on {date} at {time}"
        expected_msg = "Test commit on 2023-01-01 at 12:34:56"
        
        # 模拟创建提交时的消息生成
        commit_msg = template.format(
            date=test_time.strftime('%Y-%m-%d'),
            time=test_time.strftime('%H:%M:%S')
        )
        self.assertEqual(commit_msg, expected_msg)
    
    @patch('subprocess.check_output')
    def test_get_commit_count_error_handling(self, mock_check):
        """测试获取提交数时的异常处理"""
        mock_check.side_effect = CalledProcessError(1, 'git')
        
        with self.assertRaises(CalledProcessError):
            self._get_commit_count()
    
    def _get_commit_count(self):
        """获取Git提交计数"""
        try:
            output = check_output(['git', 'rev-list', '--count', 'HEAD'])
            return int(output.decode('utf-8'))
        except CalledProcessError as e:
            self.fail(f"获取提交数失败: {e}")


if __name__ == "__main__":
    # 如果有命令行参数，执行主程序；否则运行测试
    if len(sys.argv) > 1:
        main()
    else:
        unittest.main()
