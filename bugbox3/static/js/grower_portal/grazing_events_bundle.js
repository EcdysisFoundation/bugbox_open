import '../../sass/grower_portal.scss';

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.add-animal-btn').forEach(button => {
        button.addEventListener('click', function() {
            const eventNumber = this.dataset.eventNumber;
            const container = document.getElementById(`animal-container-${eventNumber}`);
            
            if (container) {
                const lastCard = container.querySelector('.animal-entry-card:last-child');
                if (lastCard) {
                    const newCard = lastCard.cloneNode(true);
                    
                    newCard.querySelectorAll('input, select, textarea').forEach(input => {
                        if (input.type !== 'hidden') {
                            input.value = '';
                        }
                    });
                    
                    const totalForms = document.querySelector(`#id_event_${eventNumber}-TOTAL_FORMS`);
                    if (totalForms) {
                        const formIdx = parseInt(totalForms.value);
                        
                        newCard.innerHTML = newCard.innerHTML.replace(
                            new RegExp(`event_${eventNumber}-(\\d+)-`, 'g'),
                            `event_${eventNumber}-${formIdx}-`
                        );
                        
                        container.appendChild(newCard);
                        totalForms.value = formIdx + 1;
                        
                        updateAnimalCount(eventNumber);
                    }
                }
            }
        });
    });
    
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-animal-btn') || 
            e.target.closest('.remove-animal-btn')) {
            const card = e.target.closest('.animal-entry-card');
            const deleteCheckbox = card.querySelector('input[name$="-DELETE"]');
            
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                card.style.display = 'none';
            } else {
                card.remove();
            }
            
            const eventNumber = e.target.closest('.grazing-event-card').dataset.eventNumber;
            updateAnimalCount(eventNumber);
        }
    });
    
    function updateAnimalCount(eventNumber) {
        const container = document.getElementById(`animal-container-${eventNumber}`);
        if (container) {
            const visibleCards = container.querySelectorAll('.animal-entry-card:not([style*="display: none"])');
            const countSpan = document.querySelector(`.animal-count[data-event="${eventNumber}"]`);
            if (countSpan) {
                countSpan.textContent = visibleCards.length;
            }
            
            visibleCards.forEach((card, index) => {
                const cardTitle = card.querySelector('h6');
                if (cardTitle) {
                    cardTitle.textContent = `Animal Type ${index + 1}`;
                }
                
                const removeBtn = card.querySelector('.remove-animal-btn');
                if (removeBtn) {
                    if (index === 0) {
                        removeBtn.style.display = 'none';
                    } else {
                        removeBtn.style.display = 'inline-block';
                    }
                }
            });
        }
    }
    
    document.querySelectorAll('.grazing-event-card').forEach(card => {
        const eventNumber = card.dataset.eventNumber;
        updateAnimalCount(eventNumber);
    });
});

