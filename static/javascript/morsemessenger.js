$(document).ready(function(){
  $(".step").on({
    mouseenter:function(){
      $(":first-child",this).animate({
        fontSize: '+=1em' 
      }),
      $(":last-child",this).animate({
        fontSize: '+=1em'
      });
    },
    mouseleave:function(){
      $(":first-child",this).animate({
        fontSize: '-=1em'
      }),
      $(":last-child",this).animate({
        fontSize: '-=1em'
      });
    }
  }),
  $(".imagewhatis").on({
    mouseenter:function(){
      $(this).animate({height:'+=50px',width:'+=50'})
    },
    mouseleave:function(){
      $(this).animate({height:'-=50px',width:'-=50'})
    }
  });
});
  

