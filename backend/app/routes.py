from flask import Blueprint, jsonify
from .services import get_schedule_and_scores
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 定义两个路由规则指向同一个函数
# 规则1: /api/schedule (不带日期)，用于获取当天数据
@api_bp.route('/schedule', methods=['GET'])
# 规则2: /api/schedule/<date_str> (带日期)，用于获取指定日期数据
@api_bp.route('/schedule/<date_str>', methods=['GET'])
def schedule(date_str=None):
    """
    获取赛程和比分的 API 接口。
    - 如果 date_str 未提供，则默认为今天。
    - 如果提供了 date_str，则使用该日期。
    """
    # 如果 date_str 为 None (来自 /api/schedule 的请求)
    # 我们手动格式化今天的日期
    if date_str is None:
        date_str = datetime.today().strftime('%Y-%m-%d')

    # 调用 services 函数时传入日期
    data = get_schedule_and_scores(date_str)
    return jsonify(data)