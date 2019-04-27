/**
 *
 * HTML5 Audio player with playlist
 *
 * Licensed under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Copyright 2012, Script Tutorials
 * http://www.script-tutorials.com/
 */
jQuery(document).ready(function() {

    // inner variables
    var song;
    var tracker = $('.tracker');
    var volume = $('.volume');
    var i = 1;
    function initAudio(elem) {
        var url = elem.attr('audiourl');
        var title = elem.text();
        var cover = elem.attr('cover');
        var artist = elem.attr('artist');

        $('.player .title_player').text(title);
        $('.player .artist').text(artist);
        $('.player .cover').css('background-image','url(data/' + cover+')');;

        song = new Audio('data/' + url);

        // timeupdate event listener
        song.addEventListener('timeupdate',function (){
            var curtime = parseInt(song.currentTime, 10);
            tracker.slider('value', curtime);
        });

        $('.playlist li').removeClass('active');
        elem.addClass('active');
    }
    function playAudio() {
        song.play();

        tracker.slider("option", "max", song.duration);

        $('.play').addClass('hidden');
        $('.pause').addClass('visible');
    }
    function stopAudio() {
        song.pause();

        $('.play').removeClass('hidden');
        $('.pause').removeClass('visible');
    }
    // play click
    $('.play').click(function (e) {
        e.preventDefault();
        playAudio();
    });

    // pause click
    $('.pause').click(function (e) {
        e.preventDefault();

        stopAudio();
    });

    // forward click
    $('.fwd').click(function (e) {
        e.preventDefault();

        stopAudio();

        var next = $('.playlist li.active').next();
        if (next.length == 0) {
            next = $('.playlist li:first-child');
        }
        initAudio(next);
    });

    // rewind click
    $('.rew').click(function (e) {
        e.preventDefault();

        stopAudio();

        var prev = $('.playlist li.active').prev();
        if (prev.length == 0) {
            prev = $('.playlist li:last-child');
        }
        initAudio(prev);
    });

    // show playlist
    $('.pl').click(function (e) {
        e.preventDefault();

        $('.playlist').fadeIn(300);
    });

    // playlist elements - click
    $('.playlist li').click(function () {
        stopAudio();
        initAudio($(this));
    });

    // initialization - first element in playlist
    initAudio($('.playlist li:first-child'));

    // set volume
    song.volume = 0.8;

    // initialize the volume slider
    volume.slider({
        range: 'min',
        min: 1,
        max: 100,
        value: 80,
        start: function(event,ui) {},
        slide: function(event, ui) {
            song.volume = ui.value / 100;
        },
        stop: function(event,ui) {},
    });

    // empty tracker slider
    tracker.slider({
        range: 'min',
        min: 0, max: 10,
        start: function(event,ui) {},
        slide: function(event, ui) {
            song.currentTime = ui.value;
        },
        stop: function(event,ui) {}
    });

    var player;
    time_update_interval = 0;
    // this function gets called when API is ready to use
    function onYouTubePlayerAPIReady() {
      // create the global player from the specific iframe (#video)
      player = new YT.Player('video-placeholder', {
        width: 600,
        height: 400,
        videoId: 'j5HJabRT43I',
        playerVars: {
        color: 'white',
        playlist: '5wUYa8jPQBU,px5OHMTCSBI,TslY0Tg1O5s,'
        },
        events: {
          // call this function when player is ready to use
          'onReady': initialize
        }
      });
    }
    function initialize(){

        // Update the controls on load
        updateTimerDisplay();
        updateProgressBar();

        // Clear any old interval.
        clearInterval(time_update_interval);

        // Start interval to update elapsed time display and
        // the elapsed part of the progress bar every second.
        time_update_interval = setInterval(function () {
            updateTimerDisplay();
            updateProgressBar();
        }, 1000);


        $('#volume-input').val(Math.round(player.getVolume()));
    }
    $('#play').on('click', function () {
        player.playVideo();
    });

    $('#pause').on('click', function () {
        player.pauseVideo();
    });
    // document.onkeydown = function (e) {
    //   var keyCode = e.keyCode;
    //
    //   if(keyCode == 66) { //b
    //       Reveal.slide(1, 1);
    //   }
    //
    //   //37 is left arrow and 39 is Right arrow
    //   if( keyCode == 37 || keyCode == 39 ){
    //     //e.preventDefault();
    //     stopAudio();
    //   }
    //
    //   if(keyCode == 37){
    //     page_num = page_num - 1
    //     $("#num").html(page_num);
    //   }else if(keyCode == 39){
    //     page_num = page_num + 1
    //     $("#num").html(page_num);
    //   }
    //
    //   if( page_num == 3 ){
    //     if( keyCode == 88 ){
    //       $("#num").html(keyCode);
    //       player.playVideo();
    //     }
    //   }
    //   }else if( page_num == 4 ){
    //     if(keyCode == 88) { //x
    //       $("#num").css("color","red");
    //       if( !song.paused ){
    //         e.preventDefault();
    //           $("#num").css("color","red");
    //         stopAudio();
    //       }else{
    //         e.preventDefault();
    //           $("#num").css("color","yellow");
    //         playAudio();
    //       }
    //     }else if (keyCode == 90) {//z
    //         e.preventDefault();
    //         stopAudio();
    //         var prev = $('.playlist li.active').prev();
    //         if (prev.length == 0) {
    //             prev = $('.playlist li:last-child');
    //         }
    //         initAudio(prev);
    //     }else if (keyCode == 67) {//v
    //         e.preventDefault();
    //         stopAudio();
    //         var next = $('.playlist li.active').next();
    //         if (next.length == 0) {
    //             next = $('.playlist li:first-child');
    //         }
    //         initAudio(next);
    //     }
    // }

});
// https://developers.google.com/youtube/iframe_api_reference

// global variable for the player

// Inject YouTube API script
