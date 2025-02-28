document.addEventListener('DOMContentLoaded', function() {
    // 保留原有的 DOM 元素引用
    const newTopicBtn = document.getElementById('new-topic-btn');
    const historyList = document.getElementById('history-list');
    const messagesContainer = document.getElementById('messages-container');
    const welcomeMessage = document.querySelector('.welcome-message');
    const submitTopicBtn = document.getElementById('submit-topic');
    const advancedToggle = document.getElementById('advanced-toggle');
    
    // 新增 DOM 元素引用
    const logContainer = document.getElementById('log-container');
    const logContent = document.getElementById('log-content');
    const logResizer = document.getElementById('log-resizer');
    const clearLogBtn = document.getElementById('clear-log');
    const minimizeLogBtn = document.getElementById('minimize-log');
    
    // Bootstrap 模态框
    const newTopicModal = new bootstrap.Modal(document.getElementById('newTopicModal'));
    
    // 表单字段
    const formFields = {
        prompt: document.getElementById('prompt'),
        background: document.getElementById('background'),
        rule: document.getElementById('rule'),
        max_workers: document.getElementById('max_workers'),
        split_n: document.getElementById('split_n'),
        min_length: document.getElementById('min_length'),
        max_tokens: document.getElementById('max_tokens'),
        max_retries: document.getElementById('max_retries'),
        model: document.getElementById('model'),
        system_str: document.getElementById('system_str'),
        api_key: document.getElementById('api_key'),
        base_url: document.getElementById('base_url')
    };
    
    // 当前聊天 ID
    let currentChatId = null;
    
    // 当前的 EventSource
    let eventSource = null;
    
    // 从 localStorage 加载聊天记录
    const chats = loadChats();
    renderHistoryList(chats);
    
    // 事件监听器
    newTopicBtn.addEventListener('click', openNewTopicModal);
    submitTopicBtn.addEventListener('click', handleTopicSubmit);
    advancedToggle.addEventListener('click', toggleAdvancedSettings);
    
    // 日志区域相关事件监听
    clearLogBtn.addEventListener('click', clearLog);
    minimizeLogBtn.addEventListener('click', toggleLogMinimize);
    
    // 调整大小相关事件
    let isResizing = false;
    let startY, startHeight;
    
    logResizer.addEventListener('mousedown', function(e) {
        isResizing = true;
        startY = e.clientY;
        startHeight = parseInt(document.defaultView.getComputedStyle(logContainer).height, 10);
        logResizer.classList.add('active');
        
        // 添加移动和释放事件监听
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        
        // 阻止文本选择
        e.preventDefault();
    });
    
    function handleMouseMove(e) {
        if (!isResizing) return;
        
        const newHeight = startHeight - (e.clientY - startY);
        // 设置最小和最大高度限制
        if (newHeight > 50 && newHeight < (window.innerHeight - 200)) {
            logContainer.style.height = newHeight + 'px';
        }
    }
    
    function handleMouseUp() {
        isResizing = false;
        logResizer.classList.remove('active');
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    }
    
    // 从 localStorage 加载表单值
    loadFormValues();
    
    // 清空日志
    function clearLog() {
        logContent.innerHTML = '';
    }
    
    // 最小化/最大化日志区域
    function toggleLogMinimize() {
        logContainer.classList.toggle('minimized');
        const icon = minimizeLogBtn.querySelector('i');
        
        if (logContainer.classList.contains('minimized')) {
            icon.classList.replace('bi-chevron-down', 'bi-chevron-up');
        } else {
            icon.classList.replace('bi-chevron-up', 'bi-chevron-down');
        }
    }
    
    // 添加日志
    function addLog(message, type = 'info') {
        const logItem = document.createElement('div');
        logItem.classList.add('log-item');
        
        if (type === 'error') {
            logItem.classList.add('log-error');
        } else if (type === 'success') {
            logItem.classList.add('log-success');
        }
        
        logItem.textContent = message;
        logContent.appendChild(logItem);
        
        // 滚动到底部
        logContent.scrollTop = logContent.scrollHeight;
    }
    
    // 更新进度条
    function updateProgress(current, total) {
        // 检查是否已存在进度条
        let progressContainer = document.getElementById('progress-container');
        
        if (!progressContainer) {
            progressContainer = document.createElement('div');
            progressContainer.id = 'progress-container';
            progressContainer.classList.add('progress-container');
            progressContainer.innerHTML = `
                <div class="progress">
                    <div id="progress-bar" class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <div id="progress-text" class="text-center mt-1"></div>
            `;
            logContent.appendChild(progressContainer);
        }
        
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        const percentage = Math.round((current / total) * 100);
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        progressText.textContent = `处理进度: ${current}/${total} (${percentage}%)`;
    }
    
    // 函数
    function openNewTopicModal() {
        loadFormValues();
        newTopicModal.show();
    }
    
    function toggleAdvancedSettings() {
        const icon = advancedToggle.querySelector('i');
        if (icon.classList.contains('bi-chevron-down')) {
            icon.classList.replace('bi-chevron-down', 'bi-chevron-up');
        } else {
            icon.classList.replace('bi-chevron-up', 'bi-chevron-down');
        }
    }
    
    function loadFormValues() {
        const savedValues = JSON.parse(localStorage.getItem('keepthinkFormValues')) || {};
        
        for (const [key, element] of Object.entries(formFields)) {
            if (savedValues[key]) {
                element.value = savedValues[key];
            }
        }
    }
    
    function saveFormValues() {
        const values = {};
        
        for (const [key, element] of Object.entries(formFields)) {
            values[key] = element.value;
        }
        
        localStorage.setItem('keepthinkFormValues', JSON.stringify(values));
    }
    
    function handleTopicSubmit() {
        const prompt = formFields.prompt.value.trim();
        
        if (!prompt) {
            alert('请输入具体任务');
            return;
        }
        
        saveFormValues();
        
        // 创建新聊天
        const chatId = 'chat_' + Date.now();
        const title = prompt.substring(0, 15) + (prompt.length > 15 ? '...' : '');
        
        const chatData = {
            id: chatId,
            title: title,
            prompt: prompt,
            background: formFields.background.value,
            rule: formFields.rule.value,
            max_workers: formFields.max_workers.value,
            split_n: formFields.split_n.value,
            min_length: formFields.min_length.value,
            max_tokens: formFields.max_tokens.value,
            max_retries: formFields.max_retries.value,
            model: formFields.model.value,
            system_str: formFields.system_str.value,
            api_key: formFields.api_key.value,
            base_url: formFields.base_url.value,
            timestamp: Date.now(),
            messages: []
        };
        
        // 添加用户消息
        chatData.messages.push({
            role: 'user',
            content: prompt
        });
        
        // 保存聊天到 localStorage
        saveChat(chatData);
        
        // 更新界面
        renderHistoryList(loadChats());
        selectChat(chatId);
        
        // 关闭模态框
        newTopicModal.hide();
        
        // 清空日志
        clearLog();
        
        // 确保日志区域可见
        if (logContainer.classList.contains('minimized')) {
            toggleLogMinimize();
        }
        
        // 发送请求到服务器
        sendKeepThinkRequest(chatData);
    }
    
    function sendKeepThinkRequest(chatData) {
        // 显示加载指示器
        messagesContainer.innerHTML += `
            <div class="loading-indicator">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        // 首先发送初始请求
        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: chatData.id,
                prompt: chatData.prompt,
                background: chatData.background,
                rule: chatData.rule,
                max_workers: parseInt(chatData.max_workers),
                split_n: parseInt(chatData.split_n),
                min_length: parseInt(chatData.min_length),
                max_tokens: parseInt(chatData.max_tokens),
                max_retries: parseInt(chatData.max_retries),
                model: chatData.model,
                system_str: chatData.system_str,
                api_key: chatData.api_key,
                base_url: chatData.base_url
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 连接服务器发送事件
                connectSSE(chatData.id, chatData);
            } else {
                // 处理错误
                handleRequestError(data.message);
            }
        })
        .catch(error => {
            handleRequestError('请求处理失败: ' + error.message);
        });
    }
    
    function connectSSE(chatId, chatData) {
        // 如果已有连接，先关闭
        if (eventSource) {
            eventSource.close();
        }
        
        // 创建新连接
        eventSource = new EventSource(`/stream/${chatId}`);
        
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'log') {
                    // 处理日志
                    addLog(data.content);
                } else if (data.type === 'progress') {
                    // 更新进度
                    updateProgress(data.current, data.total);
                } else if (data.type === 'result') {
                    // 处理结果
                    handleResults(data.content, chatData);
                } else if (data.type === 'error') {
                    // 处理错误
                    handleRequestError(data.message);
                } else if (data.type === 'complete') {
                    // 处理完成
                    eventSource.close();
                    addLog('处理完成！', 'success');
                    
                    // 移除加载指示器
                    const loadingIndicator = document.querySelector('.loading-indicator');
                    if (loadingIndicator) {
                        loadingIndicator.remove();
                    }
                }
            } catch (e) {
                console.error('解析错误:', e, '原始数据:', event.data);
                addLog('消息解析失败', 'error');
            }
        };
        
        eventSource.onerror = function() {
            eventSource.close();
            // console.error('SSE错误，状态:', eventSource.readyState);
            // addLog('事件流连接错误或关闭', 'error');
            addLog('SSE错误，状态:'+eventSource.readyState, 'error');
        };
    }
    
    function handleResults(results, chatData) {
        // 移除加载指示器
        const loadingIndicator = document.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
        
        // 格式化并添加AI响应
        let fullResponse = '';
        
        results.forEach(result => {
            fullResponse += `## 子任务 ${result.task_number}\n\n${result.content}\n\n`;
        });
        
        chatData.messages.push({
            role: 'assistant',
            content: fullResponse
        });
        
        // 更新localStorage
        saveChat(chatData);
        
        // 渲染消息
        renderMessage({
            role: 'assistant',
            content: fullResponse
        });
    }
    
    function handleRequestError(errorMessage) {
        // 移除加载指示器
        const loadingIndicator = document.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
        
        // 添加错误日志
        addLog(errorMessage, 'error');
        
        // 显示错误消息
        alert('处理请求时出错: ' + errorMessage);
    }
    
    function selectChat(chatId) {
        currentChatId = chatId;
        
        // 更新历史列表的活动状态
        const historyItems = document.querySelectorAll('.history-item');
        historyItems.forEach(item => {
            if (item.dataset.id === chatId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // 隐藏欢迎消息，显示消息容器
        welcomeMessage.classList.add('d-none');
        messagesContainer.classList.remove('d-none');
        
        // 加载并渲染消息
        const chats = loadChats();
        const chat = chats.find(c => c.id === chatId);
        
        if (chat) {
            renderMessages(chat.messages);
        }
    }
    
    function renderMessages(messages) {
        messagesContainer.innerHTML = '';
        
        messages.forEach(message => {
            renderMessage(message);
        });
    }
    
    function renderMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        
        if (message.role === 'user') {
            messageDiv.classList.add('user-message');
            messageDiv.textContent = message.content;
        } else {
            messageDiv.classList.add('ai-message');
            const contentDiv = document.createElement('div');
            contentDiv.classList.add('markdown-content');
            
            // 解析 Markdown
            contentDiv.innerHTML = marked.parse(message.content);
            
            // 应用语法高亮
            contentDiv.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
            
            messageDiv.appendChild(contentDiv);
        }
        
        messagesContainer.appendChild(messageDiv);
        
        // 滚动到底部
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function renderHistoryList(chats) {
        historyList.innerHTML = '';
        
        // 按时间戳排序聊天记录（最新在前）
        chats.sort((a, b) => b.timestamp - a.timestamp);
        
        chats.forEach(chat => {
            const li = document.createElement('li');
            li.classList.add('history-item');
            li.dataset.id = chat.id;
            
            if (chat.id === currentChatId) {
                li.classList.add('active');
            }
            
            li.innerHTML = `
                <span>${chat.title}</span>
                <button class="btn btn-sm text-white delete-btn">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            
            li.addEventListener('click', (e) => {
                if (!e.target.classList.contains('bi-trash') && !e.target.classList.contains('delete-btn')) {
                    selectChat(chat.id);
                }
            });
            
            const deleteBtn = li.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteChat(chat.id);
            });
            
            historyList.appendChild(li);
        });
    }
    
    function loadChats() {
        return JSON.parse(localStorage.getItem('keepthinkChats')) || [];
    }
    
    function saveChat(chatData) {
        const chats = loadChats();
        const existingIndex = chats.findIndex(c => c.id === chatData.id);
        
        if (existingIndex !== -1) {
            chats[existingIndex] = chatData;
        } else {
            chats.push(chatData);
        }
        
        localStorage.setItem('keepthinkChats', JSON.stringify(chats));
    }
    
    function deleteChat(chatId) {
        if (confirm('确定要删除此对话吗？')) {
            const chats = loadChats();
            const filteredChats = chats.filter(c => c.id !== chatId);
            localStorage.setItem('keepthinkChats', JSON.stringify(filteredChats));
            
            renderHistoryList(filteredChats);
            
            if (chatId === currentChatId) {
                currentChatId = null;
                messagesContainer.classList.add('d-none');
                welcomeMessage.classList.remove('d-none');
            }
        }
    }
});