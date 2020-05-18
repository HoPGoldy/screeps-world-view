class Bar:
    """
    简单的单行显示条

    Usage:
        bar = Bar('显示条')
        bar.update('更新内容')
        bar.close()
    """
    title = ''

    def __init__(self, title):
        """初始化显示条

        Args:
            title: 将会一直显示在该行最前部
        """
        self.title = title
        print(title, end='', flush=True)

    def update(self, info):
        """更新显示内容

        Args:
            info: 追加显示在标题后的内容
        """
        content = f'\r{" " * 100}\r{self.title} {info}'
        print(content, end='')
    
    def close(self):
        """结束本行显示
        """
        print(f'\r{" " * 100}\r{self.title} ✔')