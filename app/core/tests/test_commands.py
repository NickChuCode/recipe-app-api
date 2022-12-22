"""
Test custom Django management commands.
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    # 让运行停止一段时间的 mock，注意和类上 patch 的关系，是从内向外的，
    # 所以,patched_sleep 参数在 patched_check 之前
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        # side_effect:它既可以是一个mock对象被调用时执行的可调用的函数，
        # 也可以是一个可迭代对象或者执行时抛出的一个异常(异常类或实例)。
        # ===========================
        # 通过 side_effect 来模拟数据库服务起动，但没有完成配置时，app 连不上数据库而报错的情况
        # 根据以往的经验，首先数据库没有完成配置，会报两次 Psycopg2Error
        # 然后，数据库配置完成，但没有完成数据库的加载，会报三次 OperationalError
        # 最后，连接成功，报 True
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
