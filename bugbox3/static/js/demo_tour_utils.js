
export const TOUR_STORAGE_KEY = 'bugbox_demo_tour_active';
export const TOUR_STEP_KEY = 'bugbox_demo_tour_step';
export const TOTAL_STEPS = 17;

export function getTourState() {
    const active = sessionStorage.getItem(TOUR_STORAGE_KEY) === 'true';
    const step = parseInt(sessionStorage.getItem(TOUR_STEP_KEY) || '0', 10);
    return { active, step };
}

export function setTourState(active, step = 0) {
    sessionStorage.setItem(TOUR_STORAGE_KEY, active.toString());
    sessionStorage.setItem(TOUR_STEP_KEY, step.toString());
}

export function clearTourState() {
    sessionStorage.removeItem(TOUR_STORAGE_KEY);
    sessionStorage.removeItem(TOUR_STEP_KEY);
}

export function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }

        const observer = new MutationObserver((mutations, obs) => {
            const element = document.querySelector(selector);
            if (element) {
                obs.disconnect();
                resolve(element);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        setTimeout(() => {
            observer.disconnect();
            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
        }, timeout);
    });
}

export function waitForDataTable(tableId, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const table = document.querySelector(`#${tableId}`);
        if (!table) {
            resolve();
            return;
        }

        if (window.$ && window.$(table).hasClass('dataTable')) {
            resolve();
            return;
        }

        const checkInterval = setInterval(() => {
            if (window.$ && window.$(table).hasClass('dataTable')) {
                clearInterval(checkInterval);
                resolve();
            }
        }, 50);

        setTimeout(() => {
            clearInterval(checkInterval);
            resolve();
        }, timeout);
    });
}

export async function findTargetSampleLink(childRow) {
    if (!childRow) {
        return null;
    }
    
    let searchScope = childRow;
    const nestedTable = childRow.querySelector('table');
    if (nestedTable) {
        searchScope = nestedTable;
    } else {
        const container = childRow.querySelector('[class*="datatables"], [id*="datatables"], .container');
        if (container) {
            searchScope = container;
        } else {
            const mainTable = document.querySelector('#samples-table');
            if (mainTable) {
                searchScope = mainTable;
            }
        }
    }
    
    const mainTable = document.querySelector('#samples-table');
    const allSearchScopes = [searchScope];
    if (mainTable && !allSearchScopes.includes(mainTable)) {
        allSearchScopes.push(mainTable);
    }
    
    let allLinks = [];
    for (const scope of allSearchScopes) {
        const links = scope.querySelectorAll('a.link-success');
        allLinks.push(...Array.from(links));
    }
    
    allLinks = allLinks.filter(a => {
        const href = a.getAttribute('href') || '';
        return (href.includes('/demo/sample/') || href.includes('/samples/demo/sample/')) && !href.includes('site');
    });
    
    const seen = new Set();
    allLinks = allLinks.filter(link => {
        const href = link.getAttribute('href');
        if (seen.has(href)) return false;
        seen.add(href);
        return true;
    });
    
    if (allLinks.length === 0) {
        for (const scope of allSearchScopes) {
            const links = scope.querySelectorAll('a[href*="/demo/sample/"]');
            allLinks.push(...Array.from(links));
        }
        allLinks = allLinks.filter(a => !a.getAttribute('href')?.includes('site'));
        const seen2 = new Set();
        allLinks = allLinks.filter(link => {
            const href = link.getAttribute('href');
            if (seen2.has(href)) return false;
            seen2.add(href);
            return true;
        });
    }
    if (allLinks.length === 0) {
        for (const scope of allSearchScopes) {
            const links = scope.querySelectorAll('a[href*="/samples/demo/sample/"]');
            allLinks.push(...Array.from(links));
        }
        allLinks = allLinks.filter(a => !a.getAttribute('href')?.includes('site'));
        const seen3 = new Set();
        allLinks = allLinks.filter(link => {
            const href = link.getAttribute('href');
            if (seen3.has(href)) return false;
            seen3.add(href);
            return true;
        });
    }
    
    if (allLinks.length === 0) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const nestedTable = childRow.querySelector('table');
        const container = childRow.querySelector('[class*="datatables"], [id*="datatables"]');
        const retryScope = nestedTable || container || childRow;
        
        allLinks = retryScope.querySelectorAll('a.link-success');
        allLinks = Array.from(allLinks).filter(a => {
            const href = a.getAttribute('href') || '';
            return (href.includes('/demo/sample/') || href.includes('/samples/demo/sample/')) && !href.includes('site');
        });
        
        if (allLinks.length === 0) {
            allLinks = retryScope.querySelectorAll('a[href*="/demo/sample/"]');
            allLinks = Array.from(allLinks).filter(a => !a.getAttribute('href')?.includes('site'));
        }
        if (allLinks.length === 0) {
            allLinks = retryScope.querySelectorAll('a[href*="/samples/demo/sample/"]');
            allLinks = Array.from(allLinks).filter(a => !a.getAttribute('href')?.includes('site'));
        }
        if (allLinks.length === 0) {
            const allAnchors = retryScope.querySelectorAll('a');
            allLinks = Array.from(allAnchors).filter(a => {
                const href = a.getAttribute('href') || '';
                return (href.includes('/demo/sample/') || href.includes('/samples/demo/sample/')) && !href.includes('site');
            });
        }
    }
    
    if (allLinks.length === 0) {
        return null;
    }
    
    for (const link of allLinks) {
        const href = link.getAttribute('href') || '';
        if (href.includes('site') || !href.includes('sample')) continue;
        
        let row = link.closest('tr');
        
        if (!row || row.querySelectorAll('td').length < 2) {
            const mainTable = document.querySelector('#samples-table');
            const searchTables = mainTable ? [mainTable] : [childRow];
            
            for (const table of searchTables) {
                const allTableRows = table.querySelectorAll('table tr, table tbody tr, tbody tr');
                for (const tr of allTableRows) {
                    if (tr.contains(link) && tr.querySelectorAll('td').length >= 2) {
                        row = tr;
                        break;
                    }
                }
                if (row) break;
            }
        }
        
        if (!row) continue;
        
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length < 4) continue;
        
        const sampleType = (cells[1].textContent || '').trim().toLowerCase();
        const linkText = (link.textContent || '').replace(/\s*🐛\s*/g, '').replace(/\s*<[^>]*>\s*/g, '').trim();
        const specimenCount = (cells[3].textContent || '').trim();
        
        if (sampleType.includes('vegetation sweep') && 
            linkText.includes('T4') && 
            specimenCount === '15') {
            return link;
        }
    }
    
    for (const link of allLinks) {
        const href = link.getAttribute('href') || '';
        if (href.includes('site') || !href.includes('sample')) continue;
        
        let row = link.closest('tr');
        if (!row || row.querySelectorAll('td').length < 2) {
            const allTableRows = childRow.querySelectorAll('table tr, table tbody tr, tbody tr');
            for (const tr of allTableRows) {
                if (tr.contains(link) && tr.querySelectorAll('td').length >= 2) {
                    row = tr;
                    break;
                }
            }
        }
        if (!row) continue;
        
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length < 3) continue;
        
        const sampleType = (cells[1].textContent || '').trim().toLowerCase();
        const linkText = (link.textContent || '').replace(/\s*🐛\s*/g, '').replace(/\s*<[^>]*>\s*/g, '').trim();
        
        if (sampleType.includes('vegetation sweep') && linkText.includes('T4')) {
            return link;
        }
    }
    
    for (const link of allLinks) {
        const href = link.getAttribute('href') || '';
        if (href.includes('site') || !href.includes('sample')) continue;
        
        const linkText = (link.textContent || '').trim();
        if (linkText.includes('T4')) {
            return link;
        }
    }
    
    for (const link of allLinks) {
        const href = link.getAttribute('href') || '';
        if (!href.includes('site') && (href.includes('/demo/sample/') || href.includes('/samples/demo/sample/'))) {
            return link;
        }
    }
    
    return null;
}

export function addProgressToText(text, stepNumber) {
    const progress = `<div class="shepherd-progress"><strong>Step ${stepNumber} of ${TOTAL_STEPS}</strong></div>`;
    return progress + text;
}

export function convertPosition(position) {
    const positionMap = {
        'top': 'top',
        'bottom': 'bottom',
        'left': 'left',
        'right': 'right',
        'auto': 'auto'
    };
    return positionMap[position] || 'auto';
}

