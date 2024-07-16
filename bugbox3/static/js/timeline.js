import $ from 'jquery';

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let section = document.getElementById('timeline-section');
    section.className += 'py-5';
    let ul = document.createElement('ul');
    ul.className += 'timeline-with-icons';
    for (let i = 0; i < json_context.timeline_events.length; i++) {
      let li = document.createElement('li');
      li.className += 'timeline-item mb-5';
      li.innerHTML = `<span class="timeline-icon"><i class="bi bi-person-lines-fill"></i></span>
<h5 class="fw-bold">${json_context.timeline_events[i].event_title}</h5>
<p class="text-muted mb-2 fw-bold">${json_context.timeline_events[i].by_user__username}, ${json_context.timeline_events[i].date_time}</p>
<p class="text-muted">${json_context.timeline_events[i].body}</p>
      `
      ul.appendChild(li);
    }
    section.appendChild(ul);
})
