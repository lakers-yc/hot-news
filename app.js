/**
 * 热点追踪前端应用
 * 聚合多个财经/科技资讯源的实时热点新闻
 */

// 配置
const CONFIG = {
    API_BASE: '',  // 相对路径
    POLLING_INTERVAL: 60000,  // 1分钟轮询
    AUTO_REFRESH: true,
};

// 数据源配置 - 快讯Tab（6个）
const FAST_SOURCES = {
    cls: {
        name: '财联社',
        type: 'fast',
        icon: 'zap',
        color: '#fa0d00',
        url: 'https://www.cls.cn'
    },
    eastmoney: {
        name: '东方财富',
        type: 'fast',
        icon: 'trending-up',
        color: '#fa0d00',
        url: 'https://www.eastmoney.com'
    },
    ths: {
        name: '同花顺',
        type: 'fast',
        icon: 'bar-chart-2',
        color: '#fa0d00',
        url: 'http://www.10jqka.com.cn'
    },
    wallstreetcn: {
        name: '华尔街见闻',
        type: 'fast',
        icon: 'globe',
        color: '#fa0d00',
        url: 'http://wallstreetcn.com'
    },
    stcn: {
        name: '证券时报',
        type: 'fast',
        icon: 'newspaper',
        color: '#fa0d00',
        url: 'http://www.stcn.com'
    },
    yicai: {
        name: '第一财经',
        type: 'fast',
        icon: 'tv',
        color: '#fa0d00',
        url: 'https://www.yicai.com'
    }
};

// 数据源配置 - 热榜Tab（8个）- 财经热榜优先
const HOT_SOURCES = {
    eastmoney_hot: {
        name: '东方财富热榜',
        type: 'hot',
        icon: 'trending-up',
        color: '#fa8c16',
        url: 'https://guba.eastmoney.com'
    },
    ths_hot: {
        name: '同花顺热榜',
        type: 'hot',
        icon: 'flame',
        color: '#fa8c16',
        url: 'https://q.10jqka.com.cn/gn/'
    },
    cls_hot: {
        name: '财联社热榜',
        type: 'hot',
        icon: 'flame',
        color: '#fa8c16',
        url: 'https://www.cls.cn/hot'
    },
    yicai_hot: {
        name: '第一财经热榜',
        type: 'hot',
        icon: 'flame',
        color: '#fa8c16',
        url: 'https://www.yicai.com/news/'
    },
    stcn_hot: {
        name: '证券时报热榜',
        type: 'hot',
        icon: 'flame',
        color: '#fa8c16',
        url: 'https://news.stcn.com/'
    },
    wallstreetcn_hot: {
        name: '华尔街见闻热榜',
        type: 'hot',
        icon: 'flame',
        color: '#fa8c16',
        url: 'https://wallstreetcn.com/'
    },
    baidu: {
        name: '百度热榜',
        type: 'hot',
        icon: 'trending-up',
        color: '#fa8c16',
        url: 'https://top.baidu.com/board?tab=realtime'
    },
    toutiao: {
        name: '今日头条',
        type: 'hot',
        icon: 'flame',
        color: '#fa8c16',
        url: 'https://www.toutiao.com'
    }
};

// 兼容旧配置 - 合并所有数据源
const SOURCES = { ...FAST_SOURCES, ...HOT_SOURCES };

// 图标 SVG
const ICONS = {
    lightning: '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
    zap: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
    'trending-up': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>',
    hash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="9" x2="20" y2="9"></line><line x1="4" y1="15" x2="20" y2="15"></line><line x1="10" y1="3" x2="8" y2="21"></line><line x1="16" y1="3" x2="14" y2="21"></line></svg>',
    globe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>',
    target: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>',
    newspaper: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>',
    'bar-chart-2': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    building: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>',
    landmark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="22" x2="21" y2="22"></line><line x1="6" y1="18" x2="6" y2="11"></line><line x1="10" y1="18" x2="10" y2="11"></line><line x1="14" y1="18" x2="14" y2="11"></line><line x1="18" y1="18" x2="18" y2="11"></line><polygon points="12 2 20 7 4 7"></polygon></svg>',
    radio: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="2"></circle><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"></path></svg>',
    tv: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect><polyline points="17 2 12 7 7 2"></polyline></svg>',
    flame: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>',
    refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="m3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>',
    'external-link': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'
};

// 类型标签映射
const TYPE_LABELS = {
    fast: '快讯',
    hot: '热榜',
    tech: '科技',
    finance: '财经',
    official: '官方'
};

// 状态
let isLoading = false;
let lastUpdateTime = null;
let currentTab = 'fast';  // 当前Tab: 'fast' 或 'hot'

// DOM 元素
const newsGrid = document.getElementById('newsGrid');
const loadingOverlay = document.getElementById('loadingOverlay');
const statusDot = document.getElementById('statusDot');
const updateTimeEl = document.getElementById('updateTime');
const refreshAllBtn = document.getElementById('refreshAllBtn');

/**
 * 获取图标 SVG
 */
function getIcon(name) {
    return ICONS[name] || ICONS['zap'];
}

/**
 * 格式化相对时间
 */
function formatRelativeTime(timestamp) {
    if (!timestamp) return '';

    const now = new Date();
    const date = new Date(timestamp);
    const diff = now - date;

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (seconds < 60) {
        return '刚刚';
    } else if (minutes < 60) {
        return `${minutes}分钟前`;
    } else if (hours < 24) {
        return `${hours}小时前`;
    } else {
        return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }) +
               ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    }
}

/**
 * HTML转义函数 - 防止XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 创建新闻项 HTML
 */
function createNewsItemHTML(item, index) {
    const rankClass = index < 3 ? 'rank-num--hot' : (index < 6 ? 'rank-num--warm' : '');
    const rankNum = index + 1;
    const safeTitle = escapeHtml(item.title);
    const safeUrl = escapeHtml(item.url) || '#';

    return `
        <li class="news-item">
            <span class="rank-num ${rankClass}" aria-label="排名 ${rankNum}">${rankNum}</span>
            <div class="news-content">
                <a class="news-title"
                   href="${safeUrl}"
                   target="_blank"
                   rel="noopener noreferrer"
                   title="${safeTitle}">
                    ${safeTitle}
                </a>
            </div>
            <time class="news-time">${escapeHtml(item.time) || ''}</time>
        </li>
    `;
}

/**
 * 创建卡片 HTML
 */
function createCardHTML(sourceId, sourceConfig, data) {
    const { name, type, icon, color } = sourceConfig;
    const typeLabel = TYPE_LABELS[type] || type;
    const items = data?.items || [];
    const error = data?.error;
    const lastFetch = data?.info?.last_fetch;

    // 更新时间
    const updateTimeText = lastFetch ? formatRelativeTime(lastFetch) : '';

    let contentHTML = '';

    if (error) {
        contentHTML = `<div class="error-message">加载失败: ${error}</div>`;
    } else if (items.length === 0) {
        contentHTML = `<div class="empty-message">暂无数据</div>`;
    } else {
        contentHTML = `
            <ul class="news-list" role="list">
                ${items.map((item, index) => createNewsItemHTML(item, index)).join('')}
            </ul>
        `;
    }

    return `
        <article class="news-card" data-source="${sourceId}" aria-label="${name}">
            <header class="card-header">
                <div class="header-left">
                    <span class="source-icon" style="color: ${color}">
                        ${getIcon(icon)}
                    </span>
                    <h3 class="source-name">${name}</h3>
                    <span class="source-tag source-tag--${type}">${typeLabel}</span>
                </div>
                <div class="header-right">
                    <time class="card-time">${updateTimeText}</time>
                    <button class="refresh-btn"
                            data-source="${sourceId}"
                            aria-label="刷新${name}"
                            title="刷新">
                        ${ICONS.refresh}
                    </button>
                </div>
            </header>
            ${contentHTML}
        </article>
    `;
}

/**
 * 创建骨架屏 HTML
 */
function createSkeletonHTML(sourceId, sourceConfig) {
    const { name, type, icon, color } = sourceConfig;
    const typeLabel = TYPE_LABELS[type] || type;

    return `
        <article class="news-card" data-source="${sourceId}" aria-label="${name}">
            <header class="card-header">
                <div class="header-left">
                    <span class="source-icon" style="color: ${color}">
                        ${getIcon(icon)}
                    </span>
                    <h3 class="source-name">${name}</h3>
                    <span class="source-tag source-tag--${type}">${typeLabel}</span>
                </div>
                <div class="header-right">
                    <button class="refresh-btn loading"
                            data-source="${sourceId}"
                            aria-label="刷新${name}"
                            disabled>
                        ${ICONS.refresh}
                    </button>
                </div>
            </header>
            <div class="skeleton-container">
                ${Array(8).fill('<div class="skeleton-item"></div>').join('')}
            </div>
        </article>
    `;
}

/**
 * 渲染加载骨架屏
 */
function renderSkeleton() {
    const sources = currentTab === 'fast' ? FAST_SOURCES : HOT_SOURCES;
    let html = '';
    for (const [sourceId, sourceConfig] of Object.entries(sources)) {
        html += createSkeletonHTML(sourceId, sourceConfig);
    }
    newsGrid.innerHTML = html;
}

/**
 * 渲染新闻数据
 */
function renderNews(data) {
    const sources = currentTab === 'fast' ? FAST_SOURCES : HOT_SOURCES;
    let html = '';

    for (const [sourceId, sourceConfig] of Object.entries(sources)) {
        const sourceData = data[sourceId] || { items: [], error: '暂无数据' };
        html += createCardHTML(sourceId, sourceConfig, sourceData);
    }

    newsGrid.innerHTML = html;

    // 绑定刷新按钮事件
    bindRefreshButtons();
}

/**
 * 绑定刷新按钮事件
 */
function bindRefreshButtons() {
    const refreshBtns = document.querySelectorAll('.refresh-btn');
    refreshBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const sourceId = btn.dataset.source;
            if (sourceId) {
                await refreshSource(sourceId, btn);
            }
        });
    });
}

/**
 * 刷新单个数据源
 */
async function refreshSource(sourceId, btn) {
    if (!btn || btn.classList.contains('loading')) return;

    btn.classList.add('loading');
    btn.disabled = true;

    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/hot-news/source/${sourceId}?cache=false`);
        const result = await response.json();

        if (result.code === 200 && result.data) {
            // 从快讯或热榜配置中查找
            let sourceConfig = FAST_SOURCES[sourceId] || HOT_SOURCES[sourceId];
            if (!sourceConfig) {
                sourceConfig = SOURCES[sourceId];
            }

            const cardHTML = createCardHTML(sourceId, sourceConfig, {
                items: result.data.items,
                info: result.data.info
            });

            const card = document.querySelector(`.news-card[data-source="${sourceId}"]`);
            if (card) {
                card.outerHTML = cardHTML;
                // 重新绑定事件
                bindRefreshButtons();
            }
        }
    } catch (error) {
        console.error(`刷新 ${sourceId} 失败:`, error);
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

/**
 * 更新状态指示器
 */
function updateStatus(status, time) {
    statusDot.classList.remove('loading', 'error');

    if (status === 'loading') {
        statusDot.classList.add('loading');
        updateTimeEl.textContent = '正在加载...';
    } else if (status === 'error') {
        statusDot.classList.add('error');
        updateTimeEl.textContent = '加载失败';
    } else if (status === 'success') {
        if (time) {
            lastUpdateTime = new Date(time);
            updateTimeEl.textContent = `更新于 ${lastUpdateTime.toLocaleTimeString('zh-CN')}`;
        }
    }
}

/**
 * 显示/隐藏加载遮罩
 */
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
    isLoading = show;
}

/**
 * 切换Tab
 */
function switchTab(tab) {
    if (tab === currentTab || isLoading) return;

    currentTab = tab;

    // 更新Tab按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tab) {
            btn.classList.add('active');
        }
    });

    // 重新加载数据
    fetchTabData(tab);
}

/**
 * 获取Tab数据
 */
async function fetchTabData(tab, showOverlay = false) {
    if (isLoading) return;

    if (showOverlay) {
        showLoading(true);
    }
    updateStatus('loading');

    // 渲染骨架屏
    renderSkeleton();

    try {
        const endpoint = tab === 'fast' ? '/api/hot-news/fast' : '/api/hot-news/hot';
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`);
        const result = await response.json();

        if (result.code === 200) {
            renderNews(result.data);
            updateStatus('success', result.updateTime);
        } else {
            updateStatus('error');
            console.error('获取数据失败:', result.message);
        }
    } catch (error) {
        console.error('请求失败:', error);
        updateStatus('error');

        const sources = tab === 'fast' ? FAST_SOURCES : HOT_SOURCES;
        newsGrid.innerHTML = `
            <div class="error-message" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <p>加载数据失败，请检查网络连接或稍后重试</p>
                <button class="btn btn-primary" onclick="fetchTabData('${tab}', true)" style="margin-top: 16px;">
                    重新加载
                </button>
            </div>
        `;
    } finally {
        if (showOverlay) {
            showLoading(false);
        }
    }
}

/**
 * 获取所有热点数据
 */
async function fetchAllData(showOverlay = false) {
    // 使用新的Tab数据获取方法
    return fetchTabData(currentTab, showOverlay);
}

/**
 * 刷新所有数据
 */
async function refreshAll() {
    if (isLoading) return;

    refreshAllBtn.disabled = true;
    updateStatus('loading');

    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/hot-news/refresh`);
        const result = await response.json();

        if (result.code === 200) {
            // 刷新成功后重新获取当前Tab数据
            await fetchTabData(currentTab, false);
        } else {
            updateStatus('error');
        }
    } catch (error) {
        console.error('刷新失败:', error);
        updateStatus('error');
    } finally {
        refreshAllBtn.disabled = false;
    }
}

/**
 * 启动轮询
 */
function startPolling() {
    if (!CONFIG.AUTO_REFRESH) return;

    setInterval(() => {
        fetchTabData(currentTab, false);
    }, CONFIG.POLLING_INTERVAL);
}

/**
 * 初始化
 */
async function init() {
    // 渲染骨架屏
    renderSkeleton();

    // 绑定刷新全部按钮
    refreshAllBtn.addEventListener('click', refreshAll);

    // 加载综合热榜TOP10
    loadTop10();

    // 获取初始数据
    await fetchAllData(true);

    // 启动轮询
    startPolling();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);

// ============== 报告相关功能 ==============

let reportVisible = true;
let reportData = null;

/**
 * 切换报告显示/隐藏
 */
function toggleReport() {
    const content = document.getElementById('reportContent');
    const arrow = document.getElementById('reportArrow');

    reportVisible = !reportVisible;

    if (reportVisible) {
        content.style.display = 'block';
        arrow.innerHTML = '<polyline points="6 9 12 15 18 9"></polyline>';
    } else {
        content.style.display = 'none';
        arrow.innerHTML = '<polyline points="18 15 12 9 6 15"></polyline>';
    }
}

/**
 * 加载分析报告
 */
async function loadReport() {
    const loadingEl = document.getElementById('reportLoading');
    const bodyEl = document.getElementById('reportBody');
    const metaEl = document.getElementById('reportMeta');

    loadingEl.classList.remove('hidden');
    bodyEl.classList.add('hidden');

    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/hot-news/report`);
        const result = await response.json();

        if (result.code === 200 && result.data) {
            reportData = result.data;
            renderReport(result.data);

            if (result.updateTime) {
                metaEl.textContent = `更新于 ${result.updateTime}`;
            }

            loadingEl.classList.add('hidden');
            bodyEl.classList.remove('hidden');
        } else {
            loadingEl.innerHTML = '报告暂未生成，请稍后再试';
        }
    } catch (error) {
        console.error('加载报告失败:', error);
        loadingEl.innerHTML = '加载报告失败，请刷新重试';
    }
}

/**
 * 渲染报告
 */
function renderReport(report) {
    const bodyEl = document.getElementById('reportBody');

    // 构建日期和时间
    const dateHtml = `
        <div class="report-date">
            <strong>日期：</strong>${report.date} <strong>数据更新时间：</strong>${report.updateTime} (北京时间)
        </div>
    `;

    // 市场情绪
    const sentimentHtml = `
        <div class="report-sentiment">
            <strong>市场情绪预判：</strong>${report.marketSentiment}
        </div>
    `;

    // 分析表格
    let tableHtml = `
        <table class="report-table">
            <thead>
                <tr>
                    <th style="width: 35%">消息/政策</th>
                    <th style="width: 15%">炒作方向</th>
                    <th style="width: 10%">逻辑强度</th>
                    <th style="width: 40%">推荐关注个股</th>
                </tr>
            </thead>
            <tbody>
    `;

    if (report.analysis && report.analysis.length > 0) {
        report.analysis.forEach(item => {
            const news = item.news || {};
            const concepts = (item.concepts || []).map(c => `<span class="concept-tag">${c}</span>`).join('');
            const stocks = (item.stocks || []).map((s, i) =>
                `<span class="stock-item">${i + 1}. <span class="stock-name">${s.name}</span>(${s.code}) - <span class="stock-logic">${s.logic}</span></span>`
            ).join('');

            tableHtml += `
                <tr>
                    <td>
                        <div>${news.title || ''}</div>
                        <div style="font-size: 11px; color: #999; margin-top: 4px;">${news.source || ''} ${news.time || ''}</div>
                    </td>
                    <td>${concepts || '-'}</td>
                    <td>${item.logicStrength || '⭐⭐'}</td>
                    <td>${stocks || '暂无推荐'}</td>
                </tr>
            `;
        });
    } else {
        tableHtml += '<tr><td colspan="4" style="text-align: center; color: #999;">暂无重要新闻分析</td></tr>';
    }

    tableHtml += '</tbody></table>';

    // 异动股票
    let abnormalHtml = '';
    if (report.abnormalStocks && report.abnormalStocks.length > 0) {
        abnormalHtml = `
            <div class="abnormal-section">
                <h4>📈 近期异动股票（供参考）</h4>
                <table class="abnormal-table">
                    <tbody>
        `;

        report.abnormalStocks.slice(0, 8).forEach(stock => {
            abnormalHtml += `
                <tr>
                    <td>${stock.name}(${stock.code})</td>
                    <td>${stock.type || ''} ${stock.change_pct || 0}%</td>
                </tr>
            `;
        });

        abnormalHtml += '</tbody></table></div>';
    }

    // 策略提示
    const strategyHtml = `
        <div class="strategy-section">
            <h4>💡 策略师特别提示</h4>
            <div class="strategy-item"><strong>风险提示：</strong>${report.strategy?.risk || '注意控制仓位'}</div>
            <div class="strategy-item"><strong>操作建议：</strong>${report.strategy?.suggestion || '关注低位补涨标的'}</div>
        </div>
    `;

    // 免责声明
    const disclaimerHtml = `
        <div class="disclaimer">
            ⚠️ 风险提示：以上内容仅供参考，不构成投资建议。股市有风险，入市需谨慎。
        </div>
    `;

    bodyEl.innerHTML = dateHtml + sentimentHtml + tableHtml + abnormalHtml + strategyHtml + disclaimerHtml;
}

/**
 * 刷新报告
 */
async function refreshReport() {
    const loadingEl = document.getElementById('reportLoading');
    const bodyEl = document.getElementById('reportBody');
    const metaEl = document.getElementById('reportMeta');
    const btn = document.getElementById('refreshReportBtn');

    // 显示加载状态
    loadingEl.innerHTML = '正在生成报告，请稍候...';
    loadingEl.classList.remove('hidden');
    bodyEl.classList.add('hidden');

    // 禁用按钮
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; animation: spin 1s linear infinite;">
                <polyline points="23 4 23 10 17 10"></polyline>
                <polyline points="1 20 1 14 7 14"></polyline>
                <path d="m3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            生成中...
        `;
    }

    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/hot-news/report/refresh`);
        const result = await response.json();

        if (result.code === 200 && result.data) {
            reportData = result.data;
            renderReport(result.data);
            loadingEl.classList.add('hidden');
            bodyEl.classList.remove('hidden');

            if (result.updateTime) {
                metaEl.textContent = `更新于 ${result.updateTime}`;
            }
        } else {
            loadingEl.innerHTML = '报告生成失败: ' + (result.message || '未知错误');
        }
    } catch (error) {
        console.error('刷新报告失败:', error);
        loadingEl.innerHTML = '生成报告失败，请重试';
    } finally {
        // 恢复按钮
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle;">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <polyline points="1 20 1 14 7 14"></polyline>
                    <path d="m3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                </svg>
                刷新报告
            `;
        }
    }
}

// 不自动加载报告，等用户点击刷新按钮
// const originalInit = init;
// init = async function() {
//     await originalInit();
//     loadReport();
// };

// ============== 综合热榜TOP10功能 ==============

/**
 * 加载综合热榜TOP10数据
 */
async function loadTop10() {
    const tableUpdateTimeEl = document.getElementById('tableUpdateTime');

    try {
        const response = await fetch(`${CONFIG.API_BASE}/api/hot-news/top10`);
        const result = await response.json();

        if (result.code === 200 && result.data && result.data.items) {
            // 渲染表格式榜单
            renderTop10Table(result.data.items);

            if (result.data.updateTime && tableUpdateTimeEl) {
                const timeStr = result.data.updateTime.split(' ')[1];
                tableUpdateTimeEl.textContent = timeStr;
            }
        } else {
            renderTop10Table([]);
        }
    } catch (error) {
        console.error('加载TOP10失败:', error);
        renderTop10Table([]);
    }
}

/**
 * 渲染表格式 TOP10
 */
function renderTop10Table(items) {
    const tbody = document.getElementById('top10TableBody');

    if (!tbody || !items || items.length === 0) {
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--color-text-tertiary);">暂无数据</td></tr>';
        }
        return;
    }

    let html = '';

    items.forEach((item, index) => {
        const rank = item.rank || (index + 1);
        let rankIcon = '';
        let rankClass = '';

        if (rank === 1) {
            rankIcon = '🥇';
            rankClass = 'table-rank--1';
        } else if (rank === 2) {
            rankIcon = '🥈';
            rankClass = 'table-rank--2';
        } else if (rank === 3) {
            rankIcon = '🥉';
            rankClass = 'table-rank--3';
        } else {
            rankIcon = rank;
            rankClass = 'table-rank--default';
        }

        const heatWidth = Math.min(item.heat_score, 100);
        let heatBarClass = 'table-heat-bar--normal';
        if (heatWidth > 80) {
            heatBarClass = 'table-heat-bar--hot';
        } else if (heatWidth > 60) {
            heatBarClass = 'table-heat-bar--warm';
        }

        const safeTitle = escapeHtml(item.title);
        const safeUrl = escapeHtml(item.url) || '#';
        const sourceList = (item.sources || []).join(', ');

        html += `
            <tr>
                <td class="col-rank">
                    <span class="table-rank ${rankClass}">${rankIcon}</span>
                </td>
                <td class="col-title">
                    <a class="table-title-link"
                       href="${safeUrl}"
                       target="_blank"
                       rel="noopener noreferrer"
                       title="${safeTitle}${sourceList ? ' - 来源: ' + sourceList : ''}">
                        ${safeTitle}
                    </a>
                </td>
                <td class="col-heat">
                    <span class="table-heat-value">${item.heat_score}</span>
                </td>
                <td class="col-bar">
                    <div class="table-heat-bar-container">
                        <div class="table-heat-bar ${heatBarClass}" style="width: ${heatWidth}%"></div>
                    </div>
                </td>
                <td class="col-sources">
                    <span class="table-source-count">${item.source_count}源</span>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}