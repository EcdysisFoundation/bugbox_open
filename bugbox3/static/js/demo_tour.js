import Shepherd from 'shepherd.js';
import 'shepherd.js/dist/css/shepherd.css';
import '../css/demo_tour.css';

const TOUR_STORAGE_KEY = 'bugbox_demo_tour_active';
const TOUR_STEP_KEY = 'bugbox_demo_tour_step';

let tourObj = null;
let currentStepIndex = 0;
let isStartingTour = false;

function getTourState() {
    const active = sessionStorage.getItem(TOUR_STORAGE_KEY) === 'true';
    const step = parseInt(sessionStorage.getItem(TOUR_STEP_KEY) || '0', 10);
    return { active, step };
}

function setTourState(active, step = 0) {
    sessionStorage.setItem(TOUR_STORAGE_KEY, active.toString());
    sessionStorage.setItem(TOUR_STEP_KEY, step.toString());
}

function clearTourState() {
    sessionStorage.removeItem(TOUR_STORAGE_KEY);
    sessionStorage.removeItem(TOUR_STEP_KEY);
}

function waitForElement(selector, timeout = 5000) {
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

function waitForDataTable(tableId, timeout = 5000) {
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

const TOTAL_STEPS = 20;

function addProgressToText(text, stepNumber) {
    const progress = `<div class="shepherd-progress"><strong>Step ${stepNumber} of ${TOTAL_STEPS}</strong></div>`;
    return progress + text;
}

function convertPosition(position) {
    const positionMap = {
        'top': 'top',
        'bottom': 'bottom',
        'left': 'left',
        'right': 'right',
        'auto': 'auto'
    };
    return positionMap[position] || 'auto';
}

function getTourSteps() {
    return [
        {
            element: '.container',
            popover: {
                title: addProgressToText('Welcome to Bugbox Demo!', 1),
                description: '<p>This interactive tour will guide you through our research workflow: <strong>Experiments → Sites → Samples → Specimens</strong>.</p><p><small><i class="bi bi-keyboard"></i> Use arrow keys to navigate, or click the buttons below.</small></p>',
                position: 'top',
                showButtons: ['next', 'close'],
                nextBtnText: 'Start Tour →',
                closeBtnText: 'Skip Tour'
            },
            onHighlightStarted: async () => {
                await waitForElement('.container', 2000).catch(() => {});
            }
        },

        {
            element: '#experiments-table',
            popover: {
                title: addProgressToText('Experiments Table', 2),
                description: '<p>This table displays all experiments in the demo. Each row shows:</p><ul><li><strong>Experiment Name</strong> - Click to view details</li><strong>Abbreviation</strong> - Short code for the experiment</li><li><strong>Year(s)</strong> - When the experiment was conducted</li><li><strong>Samples</strong> - Total number of samples collected</li><li><strong>Photosampling Needed</strong> - Samples requiring photo documentation</li><li><strong>Reviewed Needed</strong> - Samples awaiting review</li></ul>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('experiments-table', 2000).catch(() => {});
            }
        },

        {
            element: '.create-button',
            popover: {
                title: addProgressToText('Create New Experiment', 3),
                description: '<p>Click the <strong>"Add Experiment"</strong> button to create a new experiment in demo mode.</p><p><em>Note: Changes in demo mode are not saved to the database - this is for demonstration purposes only.</em></p>',
                position: 'bottom'
            },
            onHighlightStarted: async () => {
                await waitForElement('.create-button', 2000).catch(() => {});
                await waitForElement('.create-button a, .create-button button', 2000).catch(() => {});
            }
        },

        {
            element: '#experiments-table',
            popover: {
                title: addProgressToText('Explore an Experiment', 4),
                description: '<p>Click on any experiment name in the table to view its details, sites, and samples.</p><p><strong>The tour will automatically continue on the next page...</strong></p>',
                position: 'bottom',
                nextBtnText: 'Click Experiment & Continue',
                onNextClick: () => {
                    const firstLink = document.querySelector('#experiments-table a[href*="demo/experiment/"]');
                    if (firstLink) {
                        setTourState(true, 5);
                        setTimeout(() => {
                            firstLink.click();
                        }, 150);
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForDataTable('experiments-table', 3000).catch(() => {});
            }
        },

        {
            element: '.card:first-of-type',
            popover: {
                title: addProgressToText('Experiment Details', 5),
                description: '<p>This card displays comprehensive information about the experiment:</p><ul><li><strong>UUID</strong> - Unique identifier</li><li><strong>Year(s)</strong> - Duration of the experiment</li><strong>Experiment Setup</strong> - Number of sites, dates per site, and sample plans</li><li><strong>Leader</strong> - Principal investigator</li><li><strong>Summary</strong> - Additional details about the experiment</li></ul>',
                position: 'bottom',
                prevBtnText: 'Back',
                onPrevClick: () => {
                    setTourState(true, 3);
                    window.location.href = '/samples/demo/experiments/';
                }
            },
            onHighlightStarted: async () => {
                await waitForElement('.card:first-of-type', 2000).catch(() => {});
            }
        },

        {
            element: '#samples-table',
            popover: {
                title: addProgressToText('Sites and Samples Table', 6),
                description: '<p>This table shows all sites in the experiment. Each row displays:</p><ul><li><strong>Site Name</strong> - Click to view site details</li><li><strong>State/Region</strong> - Geographic location</li><li><strong>County/Region</strong> - Local area</li><li><strong>Habitat Type</strong> - Environment classification</li><li><strong>Treatment</strong> - Applied treatment or condition</li></ul>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('samples-table', 3000).catch(() => {});
            }
        },

        {
            element: '#samples-table',
            popover: {
                title: addProgressToText('Expandable Sample Rows', 7),
                description: '<p>Click the <strong>arrow icon</strong> next to a site name to expand and see all samples collected at that site.</p><p>Samples are organized by:</p><ul><li><strong>Visit Date</strong> - When samples were collected</li><li><strong>Sample Type</strong> - Method used (e.g., quadrat, vegetation sweep)</li><li><strong>Transect Names</strong> - T1, T2, T3, T4, etc.</li></ul><p>Each sample shows completion status, specimen count, and review status.</p>',
                position: 'bottom'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('samples-table', 3000).catch(() => {});
            }
        },

        {
            element: 'a[href*="demo/site/create/"]',
            popover: {
                title: addProgressToText('Create New Site', 8),
                description: '<p>Click the <strong>"Create Site"</strong> button to add a new site to this experiment.</p><p>You can define location, habitat type, treatment, and other site characteristics.</p><p><em>Remember: This is demo mode - changes are not saved.</em></p>',
                position: 'bottom'
            },
            onHighlightStarted: async () => {
                await waitForElement('a[href*="demo/site/create/"]', 2000).catch(() => {});
            }
        },

        {
            element: '#samples-table',
            popover: {
                title: addProgressToText('View Site Details', 9),
                description: '<p>Click on any site name in the table to view detailed information about that site, including all visit dates and samples.</p><p><strong>The tour will automatically continue on the next page...</strong></p>',
                position: 'bottom',
                nextBtnText: 'Click Site & Continue',
                onNextClick: () => {
                    const firstSiteLink = document.querySelector('#samples-table a[href*="demo/site/"]');
                    if (firstSiteLink && !firstSiteLink.href.includes('create')) {
                        setTourState(true, 10);
                        setTimeout(() => {
                            firstSiteLink.click();
                        }, 100);
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForDataTable('samples-table', 3000).catch(() => {});
            }
        },

        {
            element: '.card:first-of-type',
            popover: {
                title: addProgressToText('Site Information', 10),
                description: '<p>This form displays comprehensive site details:</p><ul><li><strong>Location</strong> - Geographic coordinates and address</li><li><strong>Habitat Type</strong> - Environment classification</li><li><strong>Treatment</strong> - Applied treatment or condition</li><li><strong>State/County</strong> - Administrative regions</li></ul><p>You can edit these fields in demo mode (changes won\'t be saved).</p>',
                position: 'bottom',
                prevBtnText: 'Back',
                onPrevClick: () => {
                    const backLink = document.querySelector('a[href*="demo-experiment"]');
                    if (backLink) {
                        setTourState(true, 8);
                        backLink.click();
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForElement('.card:first-of-type', 2000).catch(() => {});
            }
        },

        {
            element: '#visitsAccordion',
            popover: {
                title: addProgressToText('Sample Dates (Visits)', 11),
                description: '<p>This accordion shows all dates when samples were collected at this site.</p><p><strong>Click on a date</strong> to expand and see all samples collected on that visit.</p><p>Samples are organized by transect names (T1, T2, T3, T4, etc.) and sample types (quadrat, vegetation sweep, etc.).</p><p>Each sample link shows its name, type, and completion status.</p>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForElement('#visitsAccordion', 1500).catch(() => {});
            }
        },

        {
            element: '#visitsAccordion',
            popover: {
                title: addProgressToText('View Sample Details', 12),
                description: '<p>Click on any sample name in the expanded visit dates to view detailed information about that sample, including all specimens collected.</p><p><strong>The tour will automatically continue on the next page...</strong></p>',
                position: 'bottom',
                nextBtnText: 'Click Sample & Continue',
                onNextClick: () => {
                    let sampleLink = document.querySelector('a[href*="demo-sample"]');
                    if (sampleLink) {
                        setTourState(true, 13);
                        setTimeout(() => {
                            sampleLink.click();
                        }, 100);
                    } else {
                        const firstAccordion = document.querySelector('#visitsAccordion .accordion-button');
                        if (firstAccordion && firstAccordion.classList.contains('collapsed')) {
                            firstAccordion.click();
                            setTimeout(() => {
                                sampleLink = document.querySelector('a[href*="demo-sample"]');
                                if (sampleLink) {
                                    setTourState(true, 13);
                                    setTimeout(() => {
                                        sampleLink.click();
                                    }, 100);
                                }
                            }, 300);
                        }
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForElement('#visitsAccordion', 1500).catch(() => {});
            }
        },

        {
            element: '.card:first-of-type',
            popover: {
                title: addProgressToText('Sample Details', 13),
                description: '<p>This section displays comprehensive sample information:</p><ul><li><strong>Sample Type</strong> - Collection method (quadrat, vegetation sweep, etc.)</li><li><strong>Sample Name</strong> - Transect identifier (T1, T2, etc.)</li><li><strong>Completion Status</strong> - Whether data entry is complete</li><li><strong>Sample Label</strong> - Image of the sample label (if available)</li><li><strong>Entered By</strong> - Who entered the sample data</li><li><strong>Treatment</strong> - Applied treatment</li></ul>',
                position: 'bottom',
                prevBtnText: 'Back',
                onPrevClick: () => {
                    const backLink = document.querySelector('a[href*="demo-site"]');
                    if (backLink) {
                        setTourState(true, 11);
                        backLink.click();
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForElement('.card:first-of-type', 2000).catch(() => {});
            }
        },

        {
            element: '#specimens-table',
            popover: {
                title: addProgressToText('Specimens Table', 14),
                description: '<p>This table shows all specimens collected in this sample. Each row displays:</p><ul><li><strong>Image</strong> - Thumbnail of the specimen</li><li><strong>Partial Count</strong> - Number of individuals if multiple</li><li><strong>Classification</strong> - Identified species or morphospecies</li><li><strong>Probability (Model)</strong> - AI confidence score or reviewer name</li></ul><p>Click on any specimen image or name to view detailed information.</p>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('specimens-table', 3000).catch(() => {});
            }
        },

        {
            element: '.card-header',
            popover: {
                title: addProgressToText('Specimen Management Actions', 15),
                description: '<p>Use these buttons to manage specimens:</p><ul><li><strong>Add 1 specimen</strong> - Add a single specimen with classification</li><li><strong>Add specimens w/o images</strong> - Add multiple specimens without images</li><li><strong>Upload images as specimens</strong> - Bulk upload images that will be processed as specimens</li><li><strong>Toggle Select</strong> - Select multiple specimens for batch operations</li><li><strong>Move Selected</strong> - Move selected specimens to another sample</li><li><strong>Delete Selected</strong> - Remove selected specimens</li></ul><p><em>All actions are in demo mode and won\'t be saved.</em></p>',
                position: 'bottom'
            },
            onHighlightStarted: async () => {
                const headers = document.querySelectorAll('.card-header');
                let targetHeader = null;
                for (let header of headers) {
                    const h5 = header.querySelector('h5');
                    if (h5 && h5.textContent.includes('Individual Specimens')) {
                        targetHeader = header;
                        break;
                    }
                }
                if (!targetHeader) {
                await waitForElement('.card-header', 2000).catch(() => {});
                }
            }
        },

        {
            element: '#specimens-table',
            popover: {
                title: addProgressToText('AI-Powered Classification', 16),
                description: '<p>Bugbox uses advanced AI models to automatically classify specimens:</p><ul><li><strong>AI Predictions</strong> - Model suggests species classifications</li><li><strong>Confidence Scores</strong> - Probability that the prediction is correct</li><li><strong>Review Status</strong> - Whether predictions have been confirmed or rejected</li></ul><p>Researchers can review and accept/reject AI classifications, improving accuracy over time.</p>',
                position: 'bottom'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('specimens-table', 3000).catch(() => {});
            }
        },

        {
            element: '#specimens-table',
            popover: {
                title: addProgressToText('View Specimen Details', 17),
                description: '<p>Click on any specimen image or name in the table to view detailed information, including:</p><ul><li>Full classification and taxonomy</li><li>AI predictions and confidence scores</li><li>High-resolution images</li><li>Review and acceptance status</li></ul><p><strong>The tour will automatically continue on the next page...</strong></p>',
                position: 'bottom',
                nextBtnText: 'Click Specimen & Continue',
                onNextClick: () => {
                    const specimenLink = document.querySelector('#specimens-table a[href*="demo-specimen"]');
                    if (specimenLink) {
                        setTourState(true, 18);
                        setTimeout(() => {
                            specimenLink.click();
                        }, 100);
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForDataTable('specimens-table', 3000).catch(() => {});
            }
        },

        {
            element: '.list-group-item',
            popover: {
                title: addProgressToText('Specimen Classification', 18),
                description: '<p>This section displays the complete taxonomic classification:</p><ul><li><strong>Name</strong> - Species or morphospecies name</li><li><strong>Canonical Name</strong> - Scientific name</li><li><strong>Taxonomy</strong> - Class, Order, Family, Genus, Species</li><li><strong>Determined By</strong> - Who identified the specimen (researcher or AI)</li></ul><p>Click on the species name to view more taxonomic details.</p>',
                position: 'right',
                prevBtnText: 'Back',
                onPrevClick: () => {
                    const backLink = document.querySelector('a[href*="demo-sample"]');
                    if (backLink) {
                        setTourState(true, 16);
                        backLink.click();
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForElement('.list-group', 3000).catch(() => {});
            }
        },

        {
            element: '.list-group-item',
            popover: {
                title: addProgressToText('AI Prediction & Acceptance', 19),
                description: '<p>This section shows AI model predictions:</p><ul><li><strong>AI Model Used</strong> - Version of the classification model</li><li><strong>Primary Prediction</strong> - Top species suggestion</li><li><strong>Confidence Score</strong> - Probability of correctness</li><li><strong>Secondary/Tertiary Predictions</strong> - Alternative suggestions</li><li><strong>Partial Count</strong> - Number of individuals</li><li><strong>Tags</strong> - Associated labels</li></ul><p>Click the <strong>AI Prediction button</strong> (Pending/Confirmed/Rejected) to accept or reject the AI classification.</p><p><em>In demo mode, you can interact with these features but changes won\'t be saved.</em></p>',
                position: 'right'
            },
            onHighlightStarted: async () => {
                await waitForElement('.list-group', 3000).catch(() => {});
            }
        },

        // Step 20: Image Carousel (Specimen Detail Page)
        {
            element: '#carouselControls, .col-md-7',
            popover: {
                title: addProgressToText('Specimen Images', 20),
                description: '<p>Browse high-resolution images of the specimen:</p><ul><li><strong>Image Carousel</strong> - Navigate through multiple images using arrow buttons</li><li><strong>Thumbnail Gallery</strong> - Quick access to all images</li><strong>Set Primary Image</strong> - Choose the main image for the specimen</li><li><strong>Delete Image</strong> - Remove unwanted images</li><li><strong>Upload Images</strong> - Add more images to the specimen</li></ul><p>All image management features are available in demo mode.</p><p><strong>Congratulations! You\'ve completed the tour!</strong></p>',
                position: 'left',
                nextBtnText: 'Complete Tour'
            },
            onHighlightStarted: async () => {
                try {
                    await waitForElement('#carouselControls, .col-md-7', 2000);
                } catch (e) {
                    try {
                        await waitForElement('.col-md-7', 2000);
                    } catch (e2) {
                    }
                }
            }
        }
    ];
}

function getStepsForCurrentPage() {
    const path = window.location.pathname;
    const allSteps = getTourSteps();
    
    let startIndex = 0;
    let endIndex = allSteps.length;
    
    if (path.includes('/demo/experiments') && !path.includes('/demo/experiment/')) {
        startIndex = 0;
        endIndex = 4;
    } else if (path.includes('/demo/experiment/')) {
        startIndex = 4;
        endIndex = 9;
    } else if (path.includes('/demo/site/') && !path.includes('/demo/site/create')) {
        startIndex = 9;
        endIndex = 12;
    } else if (path.includes('/demo/sample/')) {
        startIndex = 12;
        endIndex = 17;
    } else if (path.includes('/demo/specimen/')) {
        startIndex = 17;
        endIndex = 20;
    }
    
    return {
        steps: allSteps.slice(startIndex, endIndex),
        startIndex: startIndex,
        endIndex: endIndex
    };
}

function filterValidSteps(steps) {
    return steps.map((step, index) => {
        if (!step.element) return { step, valid: false };
        
        const globalStepIndex = getStepsForCurrentPage().startIndex + index;
        if (globalStepIndex === 17 || globalStepIndex === 18) {
            return { step, valid: true };
        }
        
        const element = typeof step.element === 'string' 
            ? document.querySelector(step.element)
            : step.element;
        
        if (!element) {
            if (!step.popover || !step.popover.onNextClick) {
                console.warn(`Element to highlight ${step.element} not found - skipping step`);
            }
            return { step, valid: false };
        }
        
        return { step, valid: true };
    }).filter(item => item.valid).map(item => item.step);
}

function convertStepToShepherd(step, stepIndex, globalStepIndex, tour, totalStepsCount) {
    let elementSelector = step.element;
    let actualElement = null;
    
    if (globalStepIndex === 14) {
        const headers = document.querySelectorAll('.card-header');
        for (let header of headers) {
            const h5 = header.querySelector('h5');
            if (h5 && h5.textContent.includes('Individual Specimens')) {
                actualElement = header;
                elementSelector = header;
                break;
            }
        }
    }
    else if (globalStepIndex === 17) {
        const listGroup = document.querySelector('.list-group');
        if (listGroup) {
            const allItems = Array.from(listGroup.children);
            const hrIndex = allItems.findIndex(item => item.tagName === 'HR');
            if (hrIndex > 0) {
                const firstItem = allItems[0];
                if (firstItem && firstItem.classList.contains('list-group-item')) {
                    actualElement = firstItem;
                    elementSelector = firstItem;
                } else {
                    const firstListItem = listGroup.querySelector('.list-group-item');
                    if (firstListItem) {
                        actualElement = firstListItem;
                        elementSelector = firstListItem;
                    }
                }
            } else {
                const firstItem = listGroup.querySelector('.list-group-item');
                if (firstItem) {
                    actualElement = firstItem;
                    elementSelector = firstItem;
                }
            }
        }
    }
    else if (globalStepIndex === 18) {
        const listGroup = document.querySelector('.list-group');
        if (listGroup) {
            const allItems = Array.from(listGroup.children);
            const hrIndex = allItems.findIndex(item => item.tagName === 'HR');
            if (hrIndex >= 0 && hrIndex < allItems.length - 1) {
                let aiItem = null;
                for (let i = hrIndex + 1; i < allItems.length; i++) {
                    if (allItems[i].classList.contains('list-group-item')) {
                        const text = allItems[i].textContent || '';
                        if (text.includes('AI Prediction')) {
                            aiItem = allItems[i];
                            break;
                        }
                    }
                }
                
                if (aiItem) {
                    actualElement = aiItem;
                    elementSelector = aiItem;
                } else {
                    const listItems = document.querySelectorAll('.list-group-item');
                    for (let item of listItems) {
                        const text = item.textContent || '';
                        if (text.includes('AI Prediction') || text.includes('AI Model Used')) {
                            actualElement = item;
                            elementSelector = item;
                            break;
                        }
                    }
                }
            } else {
                const listItems = document.querySelectorAll('.list-group-item');
                for (let item of listItems) {
                    if (item.textContent.includes('AI Prediction') || item.textContent.includes('AI Model Used')) {
                        actualElement = item;
                        elementSelector = item;
                        break;
                    }
                }
            }
        }
    }
    else if (typeof elementSelector === 'string' && elementSelector.includes(',')) {
        const selectors = elementSelector.split(',').map(s => s.trim());
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) {
                elementSelector = sel;
                actualElement = el;
                break;
            }
        }
    }
    else if (typeof elementSelector === 'string' && !actualElement) {
        actualElement = document.querySelector(elementSelector);
    }
    
    const attachToElement = actualElement || elementSelector;
    
    const stepConfig = {
        id: `step-${globalStepIndex}`,
        text: step.popover.description,
        title: step.popover.title,
        attachTo: attachToElement ? {
            element: attachToElement,
            on: convertPosition(step.popover.position || 'auto')
        } : undefined,
        buttons: [],
        beforeShowPromise: async function() {
            if (step.onHighlightStarted) {
                await step.onHighlightStarted();
            }
            
            if (globalStepIndex === 17) {
                const listGroup = document.querySelector('.list-group');
                if (listGroup) {
                    const parentContainer = listGroup.parentElement;
                    if (parentContainer) {
                        const allItems = Array.from(listGroup.children);
                        const hrIndex = allItems.findIndex(item => item.tagName === 'HR');
                        if (hrIndex > 0) {
                            const firstItem = allItems[0];
                            const lastItem = allItems[hrIndex - 1];
                            if (firstItem && lastItem) {
                                let wrapper = document.getElementById('tour-classification-wrapper');
                                if (!wrapper) {
                                    wrapper = document.createElement('div');
                                    wrapper.id = 'tour-classification-wrapper';
                                    wrapper.style.cssText = 'position: absolute; pointer-events: none; z-index: 10; min-width: 100px; min-height: 50px;';
                                    parentContainer.style.position = 'relative';
                                    parentContainer.appendChild(wrapper);
                                }
                                
                                await new Promise(resolve => setTimeout(resolve, 50));
                                
                                const firstRect = firstItem.getBoundingClientRect();
                                const lastRect = lastItem.getBoundingClientRect();
                                const containerRect = parentContainer.getBoundingClientRect();
                                
                                wrapper.style.top = `${firstRect.top - containerRect.top}px`;
                                wrapper.style.left = `${firstRect.left - containerRect.left}px`;
                                wrapper.style.width = `${Math.max(containerRect.width, firstRect.width)}px`;
                                wrapper.style.height = `${lastRect.bottom - firstRect.top}px`;
                                
                                wrapper.style.border = '2px solid rgba(44, 95, 45, 0.3)';
                                wrapper.style.backgroundColor = 'rgba(44, 95, 45, 0.05)';
                                
                                actualElement = wrapper;
                            }
                        }
                    }
                }
            } else if (globalStepIndex === 18) {
                const listGroup = document.querySelector('.list-group');
                if (listGroup) {
                    const parentContainer = listGroup.parentElement;
                    if (parentContainer) {
                        const allItems = Array.from(listGroup.children);
                        const hrIndex = allItems.findIndex(item => item.tagName === 'HR');
                        if (hrIndex >= 0) {
                            let aiStartIndex = -1;
                            let aiEndIndex = allItems.length;
                            
                            for (let i = hrIndex + 1; i < allItems.length; i++) {
                                if (allItems[i].classList.contains('list-group-item')) {
                                    const text = allItems[i].textContent || '';
                                    if (text.includes('AI Prediction')) {
                                        aiStartIndex = i;
                                        break;
                                    }
                                }
                            }
                            
                            if (aiStartIndex >= 0) {
                                for (let i = aiStartIndex + 1; i < allItems.length; i++) {
                                    if (allItems[i].tagName === 'HR') {
                                        if (i === allItems.length - 1 || 
                                            (allItems[i + 1] && allItems[i + 1].textContent && 
                                             allItems[i + 1].textContent.includes('Collection information'))) {
                                            aiEndIndex = i;
                                            break;
                                        }
                                    }
                                }
                                
                                const firstItem = allItems[aiStartIndex];
                                const lastItem = allItems[aiEndIndex - 1] || allItems[allItems.length - 1];
                                
                                if (firstItem && lastItem) {
                                    let wrapper = document.getElementById('tour-ai-prediction-wrapper');
                                    if (!wrapper) {
                                        wrapper = document.createElement('div');
                                        wrapper.id = 'tour-ai-prediction-wrapper';
                                        wrapper.style.cssText = 'position: absolute; pointer-events: none; z-index: 10; min-width: 200px; min-height: 100px;';
                                        if (!parentContainer.style.position) {
                                            parentContainer.style.position = 'relative';
                                        }
                                        parentContainer.appendChild(wrapper);
                                    }
                                    
                                    const updatePos = () => {
                                        const firstRect = firstItem.getBoundingClientRect();
                                        const lastRect = lastItem.getBoundingClientRect();
                                        const containerRect = parentContainer.getBoundingClientRect();
                                        
                                        if (firstRect && lastRect && containerRect) {
                                            wrapper.style.top = `${firstRect.top - containerRect.top}px`;
                                            wrapper.style.left = `${firstRect.left - containerRect.left}px`;
                                            wrapper.style.width = `${Math.max(containerRect.width, 200)}px`;
                                            wrapper.style.height = `${Math.max(lastRect.bottom - firstRect.top, 100)}px`;
                                        }
                                    };
                                    
                                    requestAnimationFrame(() => {
                                        updatePos();
                                        setTimeout(updatePos, 100);
                                    });
                                    
                                    actualElement = wrapper;
                                }
                            }
                        }
                    }
                }
            }
            
            const el = actualElement || (typeof elementSelector === 'string' 
                ? document.querySelector(elementSelector) 
                : elementSelector);
            
            if (!el) {
                console.warn(`Step ${globalStepIndex + 1}: Element not found`, elementSelector);
            }
            
            if (el) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        },
        when: {
            show: function() {
                const el = actualElement || (typeof elementSelector === 'string' 
                    ? document.querySelector(elementSelector) 
                    : elementSelector);
                
                if (el) {
                    setTimeout(() => {
                        el.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center',
                            inline: 'center'
                        });
                        
                        setTimeout(() => {
                            if (tourObj && tourObj.getCurrentStep()) {
                                const currentStep = tourObj.getCurrentStep();
                                if (currentStep && currentStep.updateStepOptions) {
                                    currentStep.el?.setAttribute('data-shepherd-positioned', 'true');
                                }
                            }
                        }, 200);
                    }, 100);
                }
            }
        }
    };

    const buttons = [];
    
    const showButtons = step.popover.showButtons || ['next', 'previous'];
    const hasClose = showButtons.includes('close');
    const hasNext = showButtons.includes('next') || step.popover.onNextClick;
    const hasPrev = (stepIndex > 0 && showButtons.includes('previous')) || step.popover.onPrevClick;
    
    if (hasPrev) {
        buttons.push({
            text: step.popover.prevBtnText || 'Back',
            action: () => {
                if (step.popover.onPrevClick) {
                    step.popover.onPrevClick();
                } else {
                    tour.back();
                }
            },
            classes: 'shepherd-button-secondary'
        });
    }

    if (hasNext && !step.popover.onNextClick) {
        const isLastStep = globalStepIndex === 19;
        buttons.push({
            text: step.popover.nextBtnText || (isLastStep ? 'Complete Tour' : 'Next'),
            action: () => {
                if (isLastStep) {
                    tour.complete();
                } else {
                    tour.next();
                }
            },
            classes: 'shepherd-button-primary'
        });
    } else if (step.popover.onNextClick) {
        buttons.push({
            text: step.popover.nextBtnText || 'Next',
            action: () => {
                step.popover.onNextClick();
            },
            classes: 'shepherd-button-primary'
        });
    }

    if (hasClose) {
        buttons.push({
            text: step.popover.closeBtnText || 'Skip Tour',
            action: () => {
                tour.cancel();
            },
            classes: 'shepherd-button-secondary'
        });
    }

    stepConfig.buttons = buttons;
    return stepConfig;
}

function createTour() {
    if (tourObj) {
        try {
            tourObj.complete();
        } catch (e) {
        }
        tourObj = null;
    }

    const { steps: pageSteps, startIndex: pageStartIndex } = getStepsForCurrentPage();
    
    const validSteps = filterValidSteps(pageSteps);
    
    if (validSteps.length === 0) {
        console.warn('No valid steps found for current page');
        return null;
    }
    

    tourObj = new Shepherd.Tour({
        useModalOverlay: false,
        defaultStepOptions: {
            cancelIcon: {
                enabled: true
            },
            classes: 'shepherd-theme-custom',
            scrollTo: true,
            scrollToHandler: (element) => {
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
                }
            },
            modalOverlayOpeningPadding: 8,
            modalOverlayOpeningRadius: 6,
            tippyOptions: {
                maxWidth: 450,
                duration: [300, 200],
                placement: 'auto',
                flipBehavior: ['top', 'bottom', 'left', 'right'],
                boundary: 'viewport',
                preventOverflow: {
                    enabled: true,
                    boundariesElement: 'viewport'
                }
            }
        }
    });


    tourObj.on('show', (event) => {
        if (event.step) {
            const stepId = event.step.id;
            const stepNumber = parseInt(stepId.replace('step-', ''), 10);
            setTourState(true, stepNumber);
            
            const oldWrapper18 = document.getElementById('tour-classification-wrapper');
            const oldWrapper19 = document.getElementById('tour-ai-prediction-wrapper');
            if (oldWrapper18 && stepNumber !== 18) oldWrapper18.remove();
            if (oldWrapper19 && stepNumber !== 19) oldWrapper19.remove();
            
            const element = event.step.options.attachTo?.element;
            if (element) {
                const el = typeof element === 'string' ? document.querySelector(element) : element;
                if (el) {
                    setTimeout(() => {
                        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        
                        if (stepNumber === 18) {
                            const wrapper = document.getElementById('tour-classification-wrapper');
                            if (wrapper && wrapper.parentElement) {
                                const listGroup = wrapper.parentElement;
                                const allItems = Array.from(listGroup.children);
                                const hrIndex = allItems.findIndex(item => item.tagName === 'HR');
                                if (hrIndex > 0) {
                                    const firstItem = allItems[0];
                                    const lastItem = allItems[hrIndex - 1];
                                    if (firstItem && lastItem) {
                                        const firstRect = firstItem.getBoundingClientRect();
                                        const lastRect = lastItem.getBoundingClientRect();
                                        const listGroupRect = listGroup.getBoundingClientRect();
                                        wrapper.style.top = `${firstRect.top - listGroupRect.top}px`;
                                        wrapper.style.height = `${lastRect.bottom - firstRect.top}px`;
                                    }
                                }
                            }
                        } else if (stepNumber === 19) {
                            const wrapper = document.getElementById('tour-ai-prediction-wrapper');
                            if (wrapper && wrapper.parentElement) {
                                const listGroup = wrapper.parentElement;
                                const allItems = Array.from(listGroup.children);
                                const hrIndex = allItems.findIndex(item => item.tagName === 'HR');
                                if (hrIndex >= 0) {
                                    let aiStartIndex = -1;
                                    let aiEndIndex = allItems.length;
                                    for (let i = hrIndex + 1; i < allItems.length; i++) {
                                        if (allItems[i].classList.contains('list-group-item')) {
                                            const text = allItems[i].textContent || '';
                                            if (text.includes('AI Prediction') || text.includes('AI Model Used') || text.includes('Primary prediction')) {
                                                if (aiStartIndex === -1) aiStartIndex = i;
                                            }
                                        } else if (allItems[i].tagName === 'HR' && aiStartIndex !== -1) {
                                            aiEndIndex = i;
                                            break;
                                        }
                                    }
                                    if (aiStartIndex >= 0) {
                                        const firstItem = allItems[aiStartIndex];
                                        const lastItem = allItems[aiEndIndex - 1] || allItems[allItems.length - 1];
                                        if (firstItem && lastItem) {
                                            const firstRect = firstItem.getBoundingClientRect();
                                            const lastRect = lastItem.getBoundingClientRect();
                                            const listGroupRect = listGroup.getBoundingClientRect();
                                            wrapper.style.top = `${firstRect.top - listGroupRect.top}px`;
                                            wrapper.style.height = `${lastRect.bottom - firstRect.top}px`;
                                        }
                                    }
                                }
                            }
                        }
                    }, 100);
                }
            }
        }
    });


    tourObj.on('complete', () => {
        const wrapper18 = document.getElementById('tour-classification-wrapper');
        const wrapper19 = document.getElementById('tour-ai-prediction-wrapper');
        if (wrapper18) wrapper18.remove();
        if (wrapper19) wrapper19.remove();
            clearTourState();
            isStartingTour = false;
        
            const completionAlert = document.createElement('div');
            completionAlert.className = 'alert alert-success alert-dismissible fade show';
            completionAlert.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10002; min-width: 300px;';
            completionAlert.innerHTML = `
                <h5><i class="bi bi-check-circle-fill"></i> Tour Complete!</h5>
                <p>You've successfully completed the Bugbox demo tour. Feel free to explore more!</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(completionAlert);
            setTimeout(() => {
                if (completionAlert.parentNode) {
                    completionAlert.remove();
                }
            }, 5000);
    });

    tourObj.on('cancel', () => {
        const wrapper18 = document.getElementById('tour-classification-wrapper');
        const wrapper19 = document.getElementById('tour-ai-prediction-wrapper');
        if (wrapper18) wrapper18.remove();
        if (wrapper19) wrapper19.remove();
        clearTourState();
        isStartingTour = false;
    });

    validSteps.forEach((step, localIndex) => {
        const globalStepIndex = pageStartIndex + localIndex;
        const shepherdStep = convertStepToShepherd(step, localIndex, globalStepIndex, tourObj, validSteps.length);
        tourObj.addStep(shepherdStep);
    });
    
    tourObj._pageStartIndex = pageStartIndex;
    tourObj._validStepsCount = validSteps.length;

    return tourObj;
}

function initTour() {
    const { active, step } = getTourState();
    
    if (active && step > 0 && !window.location.pathname.includes('/demo/experiments') && !isStartingTour) {
        setTimeout(() => {
            if (!isStartingTour) {
                startTour(step);
            }
        }, 500);
    }
}

function startTour(startStep = 0) {
    if (isStartingTour) {
        console.warn('Tour is already starting, ignoring duplicate start');
        return;
    }
    
    isStartingTour = true;
    
    if (startStep === 0) {
        clearTourState();
    }
    
    const tourInstance = createTour();
    
    if (!tourInstance) {
        console.error('Failed to create tour instance - no valid steps found');
        clearTourState();
        isStartingTour = false;
        return;
    }
    
    setTimeout(() => {
        try {
            const { startIndex: pageStartIndex } = getStepsForCurrentPage();
            
            let localStepIndex = 0;
            if (startStep >= pageStartIndex) {
                localStepIndex = startStep - pageStartIndex;
            }
            
            if (startStep === 0 || localStepIndex === 0) {
                tourInstance.start();
            } else {
                tourInstance.show(localStepIndex);
            }
            
            
            setTimeout(() => {
                isStartingTour = false;
            }, 500);
        } catch (e) {
            console.error('Error starting tour:', e);
            clearTourState();
            isStartingTour = false;
        }
    }, 300);
}


export default {
    start: startTour,
    init: initTour,
    getTourState,
    clearTourState
};

// Auto-initialize on page load
if (typeof window !== 'undefined') {
    let initTourCalled = false;
    window.addEventListener('load', () => {
        if (!initTourCalled) {
            initTourCalled = true;
            setTimeout(initTour, 1000);
        }
    });
}
