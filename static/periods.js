/**
 * 共享历史时期数据
 * 供 timeline.html 和 timeline_visualization.html 共同使用
 */

const HistoricalPeriods = {
    /**
     * 欧洲历史时期
     */
    europe: [
        { name: '史前时代', nameEn: 'Prehistoric Era', start: -2000, end: -800 },
        { name: '古风时代', nameEn: 'Archaic Period', start: -800, end: -500 },
        { name: '古典时代', nameEn: 'Classical Antiquity', start: -500, end: 476 },
        { name: '中世纪早期', nameEn: 'Early Middle Ages', start: 476, end: 1000 },
        { name: '中世纪盛期', nameEn: 'High Middle Ages', start: 1000, end: 1300 },
        { name: '中世纪晚期', nameEn: 'Late Middle Ages', start: 1300, end: 1492 },
        { name: '文艺复兴与宗教改革', nameEn: 'Renaissance & Reformation', start: 1492, end: 1648 },
        { name: '绝对主义与启蒙时代', nameEn: 'Age of Absolutism & Enlightenment', start: 1648, end: 1789 },
        { name: '漫长的十九世纪', nameEn: 'The Long 19th Century', start: 1789, end: 1914 },
        { name: '世界大战时代', nameEn: 'World Wars Era', start: 1914, end: 1945 },
        { name: '冷战时代', nameEn: 'Cold War Era', start: 1945, end: 1991 },
        { name: '当代', nameEn: 'Contemporary Era', start: 1991, end: 2100 }
    ],

    /**
     * 中国历史时期
     */
    china: [
        { name: '史前时代', nameEn: 'Prehistoric Era', start: -10000, end: -2070 },
        { name: '夏朝', nameEn: 'Xia Dynasty', start: -2070, end: -1600 },
        { name: '商朝', nameEn: 'Shang Dynasty', start: -1600, end: -1046 },
        { name: '西周', nameEn: 'Western Zhou', start: -1046, end: -771 },
        { name: '春秋时期', nameEn: 'Spring and Autumn Period', start: -770, end: -476 },
        { name: '战国时期', nameEn: 'Warring States Period', start: -475, end: -221 },
        { name: '秦朝', nameEn: 'Qin Dynasty', start: -221, end: -207 },
        { name: '西汉', nameEn: 'Western Han', start: -202, end: 8 },
        { name: '新朝', nameEn: 'Xin Dynasty', start: 9, end: 23 },
        { name: '东汉', nameEn: 'Eastern Han', start: 25, end: 220 },
        { name: '三国', nameEn: 'Three Kingdoms', start: 220, end: 280 },
        { name: '西晋', nameEn: 'Western Jin', start: 266, end: 316 },
        { name: '东晋', nameEn: 'Eastern Jin', start: 317, end: 420 },
        { name: '南北朝', nameEn: 'Northern and Southern Dynasties', start: 420, end: 589 },
        { name: '隋朝', nameEn: 'Sui Dynasty', start: 581, end: 618 },
        { name: '唐朝', nameEn: 'Tang Dynasty', start: 618, end: 907 },
        { name: '五代十国', nameEn: 'Five Dynasties and Ten Kingdoms', start: 907, end: 960 },
        { name: '北宋', nameEn: 'Northern Song', start: 960, end: 1127 },
        { name: '南宋', nameEn: 'Southern Song', start: 1127, end: 1279 },
        { name: '元朝', nameEn: 'Yuan Dynasty', start: 1271, end: 1368 },
        { name: '明朝', nameEn: 'Ming Dynasty', start: 1368, end: 1644 },
        { name: '清朝', nameEn: 'Qing Dynasty', start: 1644, end: 1912 },
        { name: '中华民国', nameEn: 'Republic of China', start: 1912, end: 1949 },
        { name: '中华人民共和国', nameEn: "People's Republic of China", start: 1949, end: 2100 }
    ],

    /**
     * 根据年份获取欧洲时期
     * @param {number} year - 年份
     * @returns {Object} 时期对象
     */
    getEuropePeriod(year) {
        return this.europe.find(p => year >= p.start && year < p.end) || 
               { name: '未知时期', nameEn: 'Unknown Period', start: year, end: year };
    },

    /**
     * 根据年份获取中国时期
     * @param {number} year - 年份
     * @returns {Object} 时期对象
     */
    getChinaPeriod(year) {
        return this.china.find(p => year >= p.start && year < p.end) || 
               { name: '未知时期', nameEn: 'Unknown Period', start: year, end: year };
    },

    /**
     * 根据年份和地区获取时期
     * @param {number} year - 年份
     * @param {string} region - 地区 ('europe' 或 'china')
     * @returns {Object} 时期对象
     */
    getPeriod(year, region) {
        if (region === 'europe' || region === 'European') {
            return this.getEuropePeriod(year);
        } else if (region === 'china' || region === 'Chinese') {
            return this.getChinaPeriod(year);
        }
        return { name: '未知时期', nameEn: 'Unknown Period', start: year, end: year };
    }
};

// 兼容 CommonJS 和浏览器环境
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HistoricalPeriods;
}
