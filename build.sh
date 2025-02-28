#!/bin/bash

# 自动版本号递增构建脚本（适配你的setup.py格式）

# 定义setup.py路径
SETUP_FILE="setup.py"

# 检查文件是否存在
if [ ! -f "$SETUP_FILE" ]; then
    echo "Error: setup.py not found!"
    exit 1
fi

# 定义精确版本号匹配模式（匹配你的格式）
VERSION_LINE_PATTERN="version=\"[0-9]+\.[0-9]+\.[0-9]+\""

# 提取当前版本号
CURRENT_VERSION=$(grep -E "^    version=" $SETUP_FILE | cut -d'"' -f2)

if [ -z "$CURRENT_VERSION" ]; then
    echo "Error: Version number not found in setup.py"
    exit 1
fi

echo "Current version: $CURRENT_VERSION"

# 拆分版本号
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# 递增补丁版本号（0.0.4 → 0.0.5）
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"

echo "New version: $NEW_VERSION"

# 精确替换版本号（保持原有格式）
sed -i.bak -E "s/(^    version=\")${CURRENT_VERSION}(\")/\1${NEW_VERSION}\2/" $SETUP_FILE

# 验证替换结果
if ! grep -q "version=\"$NEW_VERSION\"" "$SETUP_FILE"; then
    echo "Error: Version update failed"
    mv $SETUP_FILE.bak $SETUP_FILE
    exit 1
fi

# 清理备份文件
rm -f $SETUP_FILE.bak


rm -rf build dist keepthink.egg-info
#python setup.py sdist bdist_wheel
# 生成新分发包
python -m build

# 使用 twine 上传（必须指定官方源）
twine upload --repository pypi dist/*
