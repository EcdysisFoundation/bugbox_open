document.addEventListener('DOMContentLoaded', function () {
  const raceField = document.getElementById('id_race');
  if (!raceField) {
    return;
  }

  const indigenousCountryDiv = document.getElementById('div_id_race_indigenous_country');
  const raceOtherDiv = document.getElementById('div_id_race_other');
  const indigenousValue = 'indigenous_first_nations_native';
  const anotherBackgroundValue = 'another_background';

  function toggleRaceFields() {
    const race = raceField.value;

    if (indigenousCountryDiv) {
      indigenousCountryDiv.style.display = race === indigenousValue ? 'block' : 'none';
    }
    if (raceOtherDiv) {
      raceOtherDiv.style.display = race === anotherBackgroundValue ? 'block' : 'none';
    }
  }

  raceField.addEventListener('change', toggleRaceFields);
  toggleRaceFields();
});
