# 清理旧构建
rm -rf build dist keepthink.egg-info

# 生成新分发包
python -m build

# 使用 twine 上传（必须指定官方源）
twine upload --repository pypi dist/*
