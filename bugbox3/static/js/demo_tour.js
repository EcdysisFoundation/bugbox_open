import Shepherd from 'shepherd.js';
import 'shepherd.js/dist/css/shepherd.css';
import '../css/demo_tour.css';

import { 
    getTourState, 
    setTourState, 
    clearTourState,
    convertPosition
} from './demo_tour_utils.js';

import { getTourSteps } from './demo_tour_steps.js';

let tourObj = null;
let isStartingTour = false;

function getStepsForCurrentPage() {
    const path = window.location.pathname;
    const allSteps = getTourSteps(() => tourObj);
    
    let startIndex = 0;
    let endIndex = allSteps.length;
    
    if (path.includes('/demo/experiments') && !path.includes('/demo/experiment/')) {
        startIndex = 0;
        endIndex = 4;
    } else if (path.includes('/demo/experiment/')) {
        startIndex = 4;
        endIndex = 10;
    } else if (path.includes('/demo/sample/')) {
        startIndex = 9;
        endIndex = 14;
    } else if (path.includes('/demo/specimen/')) {
        startIndex = 14;
        endIndex = 17;
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
        if (globalStepIndex === 4 || globalStepIndex === 8 || 
            globalStepIndex === 14 || globalStepIndex === 15 || 
            step.element === '.card:first-of-type' || 
            step.element === '#samples-table tbody tr.child') {
            return { step, valid: true };
        }
        
        const element = typeof step.element === 'string' 
            ? document.querySelector(step.element)
            : step.element;
        
        if (!element) {
            if (step.popover && step.popover.onNextClick) {
                return { step, valid: true };
            }
            return { step, valid: false };
        }
        
        return { step, valid: true };
    }).filter(item => item.valid).map(item => item.step);
}

function convertStepToShepherd(step, stepIndex, globalStepIndex, tour, totalStepsCount) {
    let elementSelector = step.element;
    let actualElement = null;
    
    if (globalStepIndex === 8) {
        const childRow = document.querySelector('#samples-table tbody tr.child');
        if (childRow) {
            actualElement = childRow;
            elementSelector = childRow;
        } else {
            actualElement = document.querySelector('#samples-table');
            elementSelector = '#samples-table';
        }
    }
    else if (globalStepIndex === 10) {
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
    else if (globalStepIndex === 14) {
        const listGroup = document.querySelector('.list-group');
        if (listGroup) {
            const wrapper = document.getElementById('tour-classification-wrapper');
            if (wrapper) {
                actualElement = wrapper;
                elementSelector = wrapper;
            } else {
                actualElement = listGroup;
                elementSelector = listGroup;
            }
        }
    }
    else if (globalStepIndex === 15) {
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
            
            if (globalStepIndex === 8) {
                const childRow = document.querySelector('#samples-table tbody tr.child');
                if (childRow) {
                    actualElement = childRow;
                    elementSelector = childRow;
                    setTimeout(() => {
                        childRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 100);
                } else {
                    const table = document.querySelector('#samples-table');
                    if (table) {
                        actualElement = table;
                        elementSelector = table;
                    }
                }
            }
            
            if (globalStepIndex === 14) {
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
                                elementSelector = wrapper;
                            }
                        }
                    }
                }
            } else if (globalStepIndex === 15) {
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
            
            if (el) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            if (el && el !== attachToElement) {
                stepConfig.attachTo = {
                    element: el,
                    on: convertPosition(step.popover.position || 'auto')
                };
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
        const isLastStep = globalStepIndex === 16;
        buttons.push({
            text: step.popover.nextBtnText || (isLastStep ? 'Complete Tour' : 'Next'),
            action: () => {
                if (globalStepIndex === 16) {
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
            
            const oldWrapper15 = document.getElementById('tour-classification-wrapper');
            const oldWrapper16 = document.getElementById('tour-ai-prediction-wrapper');
            if (oldWrapper15 && stepNumber !== 15) oldWrapper15.remove();
            if (oldWrapper16 && stepNumber !== 16) oldWrapper16.remove();
            
            const element = event.step.options.attachTo?.element;
            if (element) {
                const el = typeof element === 'string' ? document.querySelector(element) : element;
                if (el) {
                setTimeout(() => {
                        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        
                        if (stepNumber === 15) {
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
                        } else if (stepNumber === 16) {
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


    tourObj.on('complete', (event) => {
        const wrapper15 = document.getElementById('tour-classification-wrapper');
        const wrapper16 = document.getElementById('tour-ai-prediction-wrapper');
        if (wrapper15) wrapper15.remove();
        if (wrapper16) wrapper16.remove();

        const { step: currentStep } = getTourState();
        
        let stepNumber = null;
        if (event && event.step) {
            const stepId = event.step.id;
            if (stepId) {
                stepNumber = parseInt(stepId.replace('step-', ''), 10);
            }
        }
        
        const finalStepIndex = tourObj._finalStepIndex || 16;
        const shouldShowCompletion = (currentStep === finalStepIndex) || (stepNumber === finalStepIndex);
        
            clearTourState();
            isStartingTour = false;
        
        if (shouldShowCompletion) {
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
        }
    });

    tourObj.on('cancel', () => {
        const wrapper15 = document.getElementById('tour-classification-wrapper');
        const wrapper16 = document.getElementById('tour-ai-prediction-wrapper');
        if (wrapper15) wrapper15.remove();
        if (wrapper16) wrapper16.remove();
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
    tourObj._finalStepIndex = 16;

    return tourObj;
}

function initTour() {
    const { active, step } = getTourState();
    
    if (active && step > 0 && !isStartingTour) {
        const waitTime = step === 4 ? 1000 : 500;
        setTimeout(() => {
            if (!isStartingTour) {
                if (step === 4) {
                    const checkCard = async () => {
                        for (let i = 0; i < 10; i++) {
                            const card = document.querySelector('.card');
                            if (card) {
                startTour(step);
                                return;
                            }
                            await new Promise(resolve => setTimeout(resolve, 100));
                        }
                        startTour(step);
                    };
                    checkCard();
                } else {
                    startTour(step);
                }
            }
        }, waitTime);
    }
}

function startTour(startStep = 0) {
    if (isStartingTour) {
        return;
    }
    
    isStartingTour = true;
    
    if (startStep === 0) {
        clearTourState();
    }
    
    const tourInstance = createTour();
    
    if (!tourInstance) {
        clearTourState();
        isStartingTour = false;
        return;
    }
    
    setTimeout(() => {
        try {
            const { startIndex: pageStartIndex } = getStepsForCurrentPage();
            
            const globalStepIndex = startStep > 0 ? startStep - 1 : 0;
            
            let localStepIndex = 0;
            if (globalStepIndex >= pageStartIndex) {
                localStepIndex = globalStepIndex - pageStartIndex;
                const validSteps = filterValidSteps(getStepsForCurrentPage().steps);
                if (localStepIndex >= validSteps.length) {
                    localStepIndex = 0;
                }
            }
            
            
            if (startStep === 0 || localStepIndex === 0) {
                tourInstance.start();
            } else {
                const waitTime = globalStepIndex === 4 ? 800 : 100;
                setTimeout(() => {
                    tourInstance.show(localStepIndex);
                }, waitTime);
            }
            
            
            setTimeout(() => {
                isStartingTour = false;
            }, 500);
        } catch (e) {
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
    
    window.addEventListener('popstate', () => {
        setTimeout(() => {
            if (!isStartingTour) {
                initTour();
            }
        }, 500);
    });
}
