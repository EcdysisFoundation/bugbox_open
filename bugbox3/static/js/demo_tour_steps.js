
import { 
    addProgressToText, 
    waitForElement, 
    waitForDataTable, 
    findTargetSampleLink,
    setTourState 
} from './demo_tour_utils.js';

export function getTourSteps(getTour) {
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
            element: '.create-button',
            popover: {
                title: addProgressToText('Create New Experiment', 2),
                description: '<p>Click the <strong>"Add Experiment"</strong> button to see the data-entry form for creating a new experiment.</p><p><strong>Note:</strong> Changes in demo mode are not saved to the database - this is for demonstration purposes only. When you are done, use your browser\'s Back button to continue the Tour.</p>',
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
                title: addProgressToText('Experiments Table', 3),
                description: '<p>This table will display all the Experiments your team is managing on BugBox, and it summarizes your work progress.</p><ul><li><strong>Samples</strong> – The total number of Samples in the Experiment.</li><li><strong>Photosampling Needed</strong> – The number of Samples that need to have data (photographs) uploaded.</li><li><strong>Review Needed</strong> – The number of Samples whose AI identifications haven\'t been reviewed by a human.</li></ul>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('experiments-table', 2000).catch(() => {});
            }
        },

        {
            element: '#experiments-table',
            popover: {
                title: addProgressToText('Explore the Experiment Page', 4),
                description: '<p>Click on the Experiment name in the table to view details about the Experiment.</p><p><strong>The tour will automatically continue on the next page...</strong></p>',
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
                description: '<p>This card displays an overview of the Experiment.</p><ul><li><strong>UUID</strong> – Assigned automatically by BugBox</li><li><strong>Experiment Setup</strong> – Outlines what Samples will be generated for each Site you add to the Experiment.</li><li><strong>Leader</strong> – You can designate someone to be the point of contact for Experiment.</li></ul>',
                position: 'auto',
                prevBtnText: 'Back',
                onPrevClick: () => {
                    setTourState(true, 4);
                    if (window.history.length > 1) {
                        window.history.back();
                    } else {
                        window.location.href = '/samples/demo/experiments/';
                    }
                }
            },
            onHighlightStarted: async () => {
                for (let i = 0; i < 10; i++) {
                    const card = document.querySelector('.card');
                    if (card) break;
                    await new Promise(resolve => setTimeout(resolve, 200));
                }
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        },

        {
            element: 'a[href*="demo/site/create/"]',
            popover: {
                title: addProgressToText('Create New Site', 6),
                description: '<p>Use the <strong>"Create Site"</strong> data-entry form to add a new Site to this Experiment.</p><p>In this form, you define the location, collection date(s), and other details for the Site. Then, BugBox will generate a suite of Samples for that Site, based on your Experiment Setup.</p><p><strong>Remember:</strong> This is demo mode - changes are not saved. When you are done looking at the form, use your browser\'s Back button to continue the Tour.</p>',
                position: 'left'
            },
            onHighlightStarted: async () => {
                await waitForElement('a[href*="demo/site/create/"]', 2000).catch(() => {});
            }
        },

        {
            element: '#samples-table',
            popover: {
                title: addProgressToText('Sites and Samples Table', 7),
                description: '<p>This table summarizes information for the Sites you\'ve created. In the 1000 Farms Experiment, we use 4-digit codes as Site Names to anonymize the locations. The Experiment is semi-blind, so Treatment is often listed as "unknown".</p><p>You can click on any Site name to view detailed Site information, location, and visit dates. Click the <strong>arrow icon</strong> next to any site name to expand and see all samples collected at that site.</p>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('samples-table', 3000).catch(() => {});
            }
        },

        {
            element: '#samples-table',
            popover: {
                title: addProgressToText('Expandable Sample Rows', 8),
                description: '<p>Click the down arrow on the left to expand and see all samples collected at that site. This sample table tracks work progress on each sample:</p><ul><li><strong>Sample Name</strong> – This experiment organizes samples into transects. In this demo, I\'m showing you transects 3 and 4.</li><li><strong>Completed</strong> – A green checkmark is added to a Sample manually, certifying that all Specimens have been uploaded, and the Sample is ready for data export or review.</li><li><strong>Reviewed</strong> – This column counts how many Specimens\' AI identifications have been reviewed by a human.</li></ul><p><strong>Let\'s expand a site to see its samples...</strong></p>',
                position: 'bottom',
                nextBtnText: 'Expand Site',
                onNextClick: async () => {
                    const expandButton = document.querySelector('#samples-table tbody td.details-control');
                    if (expandButton) {
                        expandButton.click();
                        let childRowFound = false;
                        for (let i = 0; i < 30; i++) {
                            let childRow = document.querySelector('#samples-table tbody tr.child');
                            if (!childRow) {
                                const detailsRow = document.querySelector('#samples-table tbody tr.details');
                                if (detailsRow) {
                                    const nextRow = detailsRow.nextElementSibling;
                                    if (nextRow && (nextRow.classList.contains('child') || 
                                        nextRow.querySelector('a[href*="sample"]') || 
                                        nextRow.innerHTML.includes('Vegetation sweep'))) {
                                        childRow = nextRow;
                                    }
                                }
                            }
                            if (!childRow) {
                                const allRows = document.querySelectorAll('#samples-table tbody tr');
                                for (let j = 0; j < allRows.length - 1; j++) {
                                    if (allRows[j].classList.contains('details') || 
                                        allRows[j].querySelector('td.details-control')) {
                                        const nextRow = allRows[j + 1];
                                        if (nextRow && (nextRow.textContent.includes('Vegetation sweep') || 
                                            nextRow.textContent.includes('Quadrat') ||
                                            nextRow.querySelector('a[href*="sample"]'))) {
                                            childRow = nextRow;
                                            break;
                                        }
                                    }
                                }
                            }
                            
                            if (childRow) {
                                childRowFound = true;
                                break;
                            }
                            await new Promise(resolve => setTimeout(resolve, 100));
                        }
                        
                        setTourState(true, 9);
                        setTimeout(() => {
                            const tour = getTour();
                            if (tour) {
                                tour.next();
                            }
                        }, childRowFound ? 400 : 800);
                    } else {
                        setTourState(true, 9);
                        setTimeout(() => {
                            const tour = getTour();
                            if (tour) {
                                tour.next();
                            }
                        }, 100);
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForDataTable('samples-table', 3000).catch(() => {});
                await new Promise(resolve => setTimeout(resolve, 300));
            }
        },

        {
            element: '#samples-table tbody tr.child',
            popover: {
                title: addProgressToText('Sample Details in Table', 9),
                description: '<p>Here you can see all samples from this site. Each sample shows:</p><ul><li><strong>Date</strong> - Collection date</li><li><strong>Sample Type</strong> - Quadrat, Vegetation sweep, etc.</li><li><strong>Sample Name</strong> - Transect identifier (T1, T2, T3, T4)</li><li><strong>Specimens</strong> - Number of specimens collected</li><li><strong>Reviewed</strong> - Review status</li><li><strong>Entered By</strong> - Data entry person</li></ul><p><strong>Let\'s view a sample to continue the tour...</strong></p>',
                position: 'bottom',
                nextBtnText: 'View Sample',
                onNextClick: async () => {
                    let childRow = null;
                    for (let i = 0; i < 20; i++) {
                        childRow = document.querySelector('#samples-table tbody tr.child');
                        
                        if (!childRow) {
                            const allRows = document.querySelectorAll('#samples-table tbody tr');
                            for (const tr of allRows) {
                                const hasColspan = tr.querySelector('td[colspan]');
                                const hasContainer = tr.querySelector('td .container');
                                
                                if (tr.classList.contains('child') || hasColspan || hasContainer) {
                                    childRow = tr;
                                    break;
                                }
                            }
                        }
                        if (childRow) break;
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                    
                    if (!childRow) {
                        alert('Error: Could not find the sample table. Please try expanding the site again.');
                        return;
                    }
                    
                    const targetLink = await findTargetSampleLink(childRow);
                    
                    if (targetLink) {
                        const href = targetLink.getAttribute('href') || '';
                        if (href.includes('site') || !href.includes('sample')) {
                            alert('Error: Found incorrect link. Please try again.');
                            return;
                        }
                        
                        setTourState(true, 10);
                        setTimeout(() => {
                            targetLink.click();
                        }, 300);
                    } else {
                        alert('Error: Could not find the sample to view. Please try again.');
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForDataTable('samples-table', 3000).catch(() => {});
                for (let i = 0; i < 30; i++) {
                    let childRow = document.querySelector('#samples-table tbody tr.child');
                    if (!childRow) {
                        childRow = document.querySelector('#samples-table tbody tr.dtrg-group');
                    }
                    if (!childRow) {
                        const detailsRow = document.querySelector('#samples-table tbody tr.details');
                        if (detailsRow && detailsRow.nextElementSibling) {
                            childRow = detailsRow.nextElementSibling;
                        }
                    }
                    
                    if (childRow) break;
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        },

        {
            element: '.card:first-of-type',
            popover: {
                title: addProgressToText('Sample Details', 10),
                description: '<p>This section displays comprehensive sample information, which you define when you create the Experiment and Site.</p><p>With free access to the full Research tools, you can add a photo of your Sample label, toggle "Completed" status when all the data is uploaded, and log which user uploaded the Sample.</p>',
                position: 'auto',
                prevBtnText: 'Back',
                onPrevClick: () => {
                    setTourState(true, 9);
                    if (window.history.length > 1) {
                        window.history.back();
                    } else {
                        window.location.href = document.referrer || '/samples/demo/experiments/';
                    }
                }
            },
            onHighlightStarted: async () => {
                await waitForElement('.card', 3000).catch(() => {});
                await new Promise(resolve => setTimeout(resolve, 300));
            }
        },

        {
            element: '.card-header',
            popover: {
                title: addProgressToText('Specimen Management Actions', 11),
                description: '<p>Use these buttons to manage specimens:</p><ul><li><strong>Add specimens w/o images</strong> – This button is for adding Specimens you don\'t want to photograph, such as Specimens that belong to taxonomic outgroups (worms, snails, etc).</li><li><strong>Upload images as specimens</strong> – This is the most important tool on BugBox! You can upload a batch of individual photographs here.</li><li><strong>Toggle/Move/Delete</strong> – These buttons work with the checkboxes in the Specimens table below, to fix errors you might make during upload.</li></ul><p><strong>All actions are in demo mode and won\'t be saved.</strong></p>',
                position: 'left'
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
                title: addProgressToText('Specimens Table', 12),
                description: '<p>Once you upload Specimens, this table will appear to display details about your Specimens.</p><ul><li><strong>Partial Count</strong> – If you have too many of a species to photograph them all, you can photograph just one and report a partial count for the rest of them.</li><li><strong>Classification</strong> – This tells you the identification that BugBox is using for this Specimen.</li><li><strong>Probability (Model)</strong> – This column tells you which AI model or user assigned the Classification, and it displays the probability (a measure of confidence) for an AI classification.</li></ul>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('specimens-table', 3000).catch(() => {});
            }
        },

        {
            element: '#specimens-table',
            popover: {
                title: addProgressToText('AI-Powered Classification', 13),
                description: '<p>BugBox uses advanced AI models to automatically classify specimens. The model runs inference on our local server every 15 minutes, so classifications will not show up immediately after upload.</p><p>Researchers can review and correct AI classifications.</p>',
                position: 'top'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('specimens-table', 3000).catch(() => {});
            }
        },

        {
            element: '#specimens-table',
            popover: {
                title: addProgressToText('View Specimen Details', 14),
                description: '<p>Click on any specimen image or name in the table to view detailed information, including:</p><ul><li>Full classification and taxonomy</li><li>AI predictions and confidence scores</li><li>High-resolution images</li><li>Review and acceptance status</li></ul>',
                position: 'top',
                showButtons: ['previous', 'close'],
                prevBtnText: 'Back'
            },
            onHighlightStarted: async () => {
                await waitForDataTable('specimens-table', 3000).catch(() => {});
            }
        },

        {
            element: '.list-group-item',
            popover: {
                title: addProgressToText('Specimen Classification', 15),
                description: '<p>This section displays the complete taxonomic classification:</p><ul><li><strong>Name</strong> - Species or morphospecies name</li><li><strong>Canonical Name</strong> - Scientific name</li><li><strong>Taxonomy</strong> - Class, Order, Family, Genus, Species</li><li><strong>Determined By</strong> - Who identified the specimen (researcher or AI)</li></ul><p>Click on the species name to view more taxonomic details.</p>',
                position: 'auto',
                prevBtnText: 'Back',
                onPrevClick: () => {
                    setTourState(true, 14);
                    if (window.history.length > 1) {
                        window.history.back();
                    } else {
                        const backLink = document.querySelector('a[href*="demo-sample"]');
                        if (backLink) {
                            backLink.click();
                        }
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
                title: addProgressToText('AI Prediction & Acceptance', 16),
                description: '<p>This section shows AI model predictions:</p><ul><li><strong>Primary Prediction</strong> - Top Morphospecies suggestion</li><li><strong>Confidence Score</strong> - Probability of correctness</li><li><strong>Secondary/Tertiary Predictions</strong> - Alternative suggestions</li></ul><p>Click the AI Prediction button (Pending/Confirmed/Rejected) to accept or reject the AI classification.</p><p><strong>In demo mode, you can interact with these features but changes won\'t be saved.</strong></p>',
                position: 'auto'
            },
            onHighlightStarted: async () => {
                await waitForElement('.list-group', 3000).catch(() => {});
            }
        },

        {
            element: '#carouselControls, .col-md-7',
            popover: {
                title: addProgressToText('Specimen Images', 17),
                description: '<p>Browse high-resolution images of the specimen:</p><ul><li><strong>Image Carousel</strong> - Navigate through multiple images using arrow buttons</li><li><strong>Thumbnail Gallery</strong> - Quick access to all images</li><strong>Set Primary Image</strong> - Choose the main image for the specimen</li><li><strong>Delete Image</strong> - Remove unwanted images</li><li><strong>Upload Images</strong> - Add more images to the specimen</li></ul><p>All image management features are available in demo mode.</p><p><strong>Congratulations! You\'ve completed the tour!</strong></p>',
                position: 'auto',
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

