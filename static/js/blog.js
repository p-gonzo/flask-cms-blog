function setPostsCalendarDate() {
  const postsCreated = [ ...document.getElementsByClassName('post-created-utc-string')];
  postsCreated.forEach(date => {
    date.innerHTML = moment.utc(date.innerHTML).local().calendar();
  });
}

function hasClass(elem, className) {
  return elem.className.split(' ').indexOf(className) > -1;
}

document.addEventListener('click', evt => {
  if (hasClass(evt.target, 'close')) {
    evt.target.parentNode.remove();
  }
}, false);

window.onscroll = function() {myFunction()};

let navbar;
let contentContainer;
let stickyThreshold; 

function myFunction() {
  if (window.pageYOffset >= stickyThreshold) {
    navbar.classList.add('sticky-navbar');
  } else {
    navbar.classList.remove('sticky-navbar');
  }
}

// Fire after the DOM has loaded
setTimeout(() => {
  setPostsCalendarDate();
  navbar = document.getElementById('navbar');
  contentContainer = document.getElementById('main-content-container');
  stickyThreshold = navbar.offsetTop;
}, 0);