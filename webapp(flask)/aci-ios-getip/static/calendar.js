function saveDraft() {

}

function openCalendar() {
    document.getElementById('calendarMode').style.display = 'flex';
}

function selectDateTime() {
    const startDate = document.getElementById('startDatePicker').value;
    const startTime = document.getElementById('startTimePicker').vlaue;
    const endDate = document.getElementById('endDatePicker').value;
    const endTime = document.getElementById('endTimePicker').value;

    if ((startDate && startTime && endDate && endTime)) {
        document.getElementById('selectedDateTime').textContent = '${startDate} ${startTime} - ${endDate} ${endTime}';
        document.getElementById('calendarModel').style.display = 'none';
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('calendarModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
