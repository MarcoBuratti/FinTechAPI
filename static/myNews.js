$('body').imagesLoaded(function() {
    $('.masonry-wrapper').masonry({
      itemSelector: '.card',
      columnWidth: '.card',
      gutter: '.gutter',
      percentPosition: true,
    });
  });
  
  $(window).trigger('resize');