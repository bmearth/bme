function textCounter(textarea, countdown, maxlimit)
{
	left = maxlimit - textarea.value.length
	if(textarea.value.length >= maxlimit) {
		textarea.value = textarea.value.substring(0, maxlimit);
		countdown.text(left + " Characters Available");
	} else {
		countdown.text(left + " Characters Available");
      	}
}

$(document).ready(function() {
	$('#repeat-days-row').hide();
	//textCounter($("#id_print_description"), $("#print_description_countdown"), 150);		

	if($("#existing").val() == "true") {
		$('#all-day-event-row').hide();
		$('#repeats-row').hide();
		$('#repeat-days-row').hide();
		$('#start-row').hide();
		$('#end-row').hide();
	}
	$("#id_repeats").click(function () {
		if(this.checked) {
			$('#repeat-days-row').show();
			$('#id_start_time_0').hide();
			$('#id_end_time_0').hide();
			if($("#id_all_day").is(':checked')) {
				$('#start-row').hide();
				$('#end-row').hide();
			}
		} else {
			$('#repeat-days-row').hide();
			$('#id_start_time_0').show();
			$('#id_end_time_0').show();
			$('#start-row').show();
			if($("#id_all_day").is(':checked')) {
			} else {
				$('#end-row').show();
			}
		}
	});
	
	$("#id_all_day").click(function () {
		if(this.checked) {
			$('#id_start_time_1').hide();
			$('#id_end_time_1').hide();
			$("label[for='id_start_time_0']").text('Day'); 
			if($("#id_repeats").is(':checked')) {
				$('#start-row').hide();
				$('#end-row').hide();
			} else {
				$('#end-row').hide();
			}
		} else {
			$('#id_start_time_1').show();
			$('#id_end_time_1').show();
			$('#start-row').show();
			$('#end-row').show();
			$("label[for='id_start_time_0']").text('Start'); 
		}
	});
	
	$("#id_print_description").keyup(function(){ 
		textCounter(this, $("#print_description_countdown"), 150);		
	});
	
	$("#id_description").keyup(function(){ 
		textCounter(this, $("#online_description_countdown"), 2000);		
	});
});
