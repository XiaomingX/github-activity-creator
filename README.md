## GitHub活动生成器

这是一个能快速美化你的GitHub贡献图表的小工具。

## 重要提示
这个工具不是为了鼓励作弊，而是针对那些过分看重GitHub个人主页上贡献图表的人。实际上，这个图表并不能真实反映一个程序员的专业能力。

## 工具效果
- 使用前：贡献图表看起来比较空白
![alt text](before.png)
- 使用后：贡献图表显示丰富的活动记录
![alt text](after.png)

## 使用方法
1. 先创建一个空的GitHub仓库（不要初始化）
2. 下载contribute.py脚本
3. 运行命令：`python contribute.py --repository=git@github.com:用户名/仓库名.git`

## 主要功能
- 自动生成过去一年的提交记录
- 每天可以生成0-20次提交
- 可以设置是否在周末提交
- 可以自定义提交频率和数量

## 个性化设置
- 调整每日提交次数：使用`--max_commits`参数
- 设置提交频率：使用`--frequency`参数
- 跳过周末提交：使用`--no_weekends`参数
- 自定义时间范围：使用`--days_before`和`--days_after`参数

## 使用要求
- 需要安装Python和Git
- 确保GitHub邮箱与本地Git邮箱设置一致

## 常见问题解决
1. 活动记录没有立即更新：需要等待几分钟让GitHub重新统计
2. 私有仓库的贡献没显示：需要在GitHub设置中允许显示私有贡献
3. 邮箱配置问题：确保本地Git邮箱与GitHub账号邮箱一致

如果遇到其他问题，可以在项目Issues中提出。
