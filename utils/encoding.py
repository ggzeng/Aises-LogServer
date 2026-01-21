"""编码处理工具函数"""

import logging

logger = logging.getLogger(__name__)


def decode_request_body(body: bytes, content_type: str | None = None) -> str:
    """
    智能解码请求体，支持 UTF-8 和 GBK 编码

    Args:
        body: 原始请求体字节
        content_type: Content-Type 头

    Returns:
        解码后的字符串
    """
    # 首先尝试从 Content-Type 头获取编码
    encoding = "utf-8"  # 默认编码
    if content_type:
        # 解析 Content-Type，例如: "application/json; charset=gbk"
        for part in content_type.split(";"):
            part = part.strip().lower()
            if part.startswith("charset="):
                encoding = part.split("=", 1)[1].strip()
                logger.debug(f"从 Content-Type 检测到编码: {encoding}")
                break

    # 尝试使用检测到的编码或默认 UTF-8 解码
    try:
        decoded = body.decode(encoding)
        logger.debug(f"成功使用 {encoding} 编码解码请求体")
        return decoded
    except (UnicodeDecodeError, LookupError) as e:
        logger.debug(f"使用 {encoding} 解码失败: {e}，尝试其他编码")

    # 如果 UTF-8 失败，尝试常见编码
    encodings_to_try = ["gbk", "gb2312", "gb18030", "big5", "shift_jis"]

    for enc in encodings_to_try:
        try:
            decoded = body.decode(enc)
            logger.info(f"成功使用 {enc} 编码解码请求体（UTF-8 失败后的回退）")
            return decoded
        except (UnicodeDecodeError, LookupError):
            continue

    # 如果所有编码都失败，使用 UTF-8 并替换错误字符
    logger.warning("所有编码尝试失败，使用 UTF-8 并替换错误字符")
    return body.decode("utf-8", errors="replace")
