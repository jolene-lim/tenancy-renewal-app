// date
$(function() {
    dates = document.getElementsByClassName("date");
    for (let date of dates) {
        dateText = date.innerHTML;
        dateDate = new Date(dateText);
        date.innerHTML = dateDate.toLocaleString('en-SG');
    }
});

// next and prev page
$(function() {
    var leftOffset = 0;
    $(".pagebtn.next").on("click", function(e) {
        leftOffset += $(this).parents(".slide").next().offset().left;
        $(".main").scrollLeft( leftOffset );
        return false;
    });

    $(".pagebtn.prev").on("click", function(e) {
        leftOffset += $(this).parents(".slide").prev().offset().left;
        $(".main").scrollLeft( leftOffset );
        return false;
    });
});

// checkbox
$(function() {
    $('input[name="verification"]').bind('click', function() {
        var verifyText = $(this).next();
        if ($(this).prop('checked')){
            verifyText.html('Verified!');
            $(this).parent().css("background-color", "#d1d8e0");
        } else {
            verifyText.html('Not Verified');
            $(this).parent().css("background-color", "#fc5c65");
        }
    });
    $('input[name="renewal"]').bind('click', function() {
        var verifyText = $(this).next();
        if ($(this).prop('checked')){
            verifyText.html('Eligible for Renewal');
            $(this).parent().css("background-color", "#d1d8e0");
        } else {
            verifyText.html('Ineligible for Renewal');
            $(this).parent().css("background-color", "#fc5c65");
        }
    });
});

// save request
$(function() {
    $('input[name="save"]').bind('click', function() {
        console.log("yes");
        var form = $(this).parents(".slide").children('.info');
        var id = form.attr('id');

        var income = form.find('input[name="income"]').val();
        var verified = form.find('input[name="verification"]').prop('checked');
        var renew = form.find('input[name="renewal"]').prop('checked');

        $.ajax({
            url: "/post_updates",
            type: "get",
            data: {id: id, income: income, verified: verified, renew: renew},
            success: function(response) {
            $("<div id='status'>" + response + "</div>").addClass('status').appendTo($("body"));
            },
            error: function(xhr) {
            }
        });
    })  
});

// archive
$(function() {
    $('input[name="archive"]').bind('click', function() {
        var form = $(this).parents(".slide").children('.info');
        var id = form.attr('id');

        $.ajax({
            url: "/archive",
            type: "get",
            data: {id: id},
            success: function(response) {
            $("<div id='status'>" + response + "</div>").addClass('status').appendTo($("body"));
            },
            error: function(xhr) {
            }
        });
    })  
});

setTimeout(function() {
  $("#status").fadeOut().empty();
}, 5000);
