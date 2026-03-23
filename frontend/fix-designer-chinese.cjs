const fs = require('fs');
const path = require('path');

const translations = {
    '已复制!': 'Copied',
    '是否必填': 'Required?',
    '暂无数据': 'No data',
    '操作': 'Operation',
    '点击添加手写签名': 'Click to add signature',
    '请在虚线框内书写': 'Please write within the box',
    '重置': 'Reset',
    '确定': 'OK',
    '面板': 'Panel',
    '标签页': 'Tabs',
    '子表单': 'Subform',
    '评分': 'Rate',
    '选择器': 'Select',
    '输入框': 'Input',
    '单选框': 'Radio',
    '格子': 'Col',
    '按钮': 'Button',
    '树形选择': 'TreeSelect',
    '日期区间': 'DateRange',
    '选项卡': 'TabPane',
    '分组': 'Group',
    '上传': 'Upload',
    '多选框': 'Checkbox',
    '文字': 'Text',
    '标签': 'Tag',
    '卡片': 'Card',
    '多行输入框': 'Textarea',
    '表格布局': 'TableLayout',
    '密码输入框': 'Password',
    '提示': 'Alert',
    '级联选择器': 'Cascader',
    '时间区间': 'TimeRange',
    '颜色选择器': 'ColorPicker',
    '日期': 'Date',
    '计数器': 'InputNumber',
    '图片': 'Image',
    '栅格布局': 'Row',
    '手写签名': 'Signature',
    '富文本框': 'Editor',
    '时间': 'Time',
    '穿梭框': 'Transfer',
    '分割线': 'Divider',
    '树形控件': 'Tree',
    '开关': 'Switch',
    '间距': 'Space',
    '表格表单': 'TableForm',
    '滑块': 'Slider',
    '标题': 'Title',
    '折叠面板': 'Collapse',
    '基础组件': 'Basic',
    '子表单组件': 'Subform',
    '辅助组件': 'Auxiliary',
    '布局组件': 'Layout',
    '第{index}页': 'Page {index}',
    '添加': 'Add',
};

// Also add variants that might have been partially replaced
const variants = {
    '多行Input': 'Textarea',
    '密码Input': 'Password',
    '级联Select': 'Cascader',
    '颜色Select': 'ColorPicker',
    '折叠Panel': 'Collapse',
    'Subform组件': 'Subform',
};

Object.assign(translations, variants);

// Sort keys by length descending to prevent partial replacements
const sortedCnKeys = Object.keys(translations).sort((a, b) => b.length - a.length);

function unicodeEscape(str) {
    return str.split('').map(char => {
        const code = char.charCodeAt(0).toString(16).toUpperCase();
        if (code.length <= 2) return char;
        return '\\u' + '0000'.substring(0, 4 - code.length) + code;
    }).join('');
}

function unicodeEscapeLower(str) {
    return str.split('').map(char => {
        const code = char.charCodeAt(0).toString(16).toLowerCase();
        if (code.length <= 2) return char;
        return '\\u' + '0000'.substring(0, 4 - code.length) + code;
    }).join('');
}

function patchFiles(directory) {
    const files = fs.readdirSync(directory);
    files.forEach(file => {
        const fullPath = path.join(directory, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
            if (file !== 'locale') {
                patchFiles(fullPath);
            }
        } else if (file.endsWith('.js') || file.endsWith('.vue') || file.endsWith('.html')) {
            let content = fs.readFileSync(fullPath, 'utf8');
            let changed = false;

            for (const cn of sortedCnKeys) {
                const en = translations[cn];
                // Literal
                if (content.includes(cn)) {
                    content = content.split(cn).join(en);
                    changed = true;
                }

                // Unicode escapes (common in dist files)
                const escUpper = unicodeEscape(cn);
                if (content.includes(escUpper)) {
                    content = content.split(escUpper).join(en);
                    changed = true;
                }
                const escLower = unicodeEscapeLower(cn);
                if (content.includes(escLower)) {
                    content = content.split(escLower).join(en);
                    changed = true;
                }
            }

            if (changed) {
                fs.writeFileSync(fullPath, content, 'utf8');
                console.log(`Patched: ${fullPath}`);
            }
        }
    });
}

const designerPath = path.join(__dirname, 'node_modules', '@form-create', 'designer');
if (fs.existsSync(designerPath)) {
    console.log('Patching @form-create/designer...');
    patchFiles(path.join(designerPath, 'src'));
    patchFiles(path.join(designerPath, 'dist'));
} else {
    console.error('Could not find @form-create/designer in node_modules');
}
