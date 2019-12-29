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

window.onscroll = function() {handleStickNav()};

let navbar;
let navbarBrands;
let contentContainer;
let stickyThreshold;

function handleStickNav() {
  if (window.pageYOffset >= stickyThreshold) {
    navbar.classList.add('sticky-navbar');
    navbarBrands.forEach(elem => elem.style.display = 'flex');
  } else {
    navbar.classList.remove('sticky-navbar');
    navbarBrands.forEach(elem => elem.style.display = 'none');
  }
}

// Fire after the DOM has loaded
setTimeout(() => {
  setPostsCalendarDate();
  navbar = document.getElementById('navbar');
  navbarBrands = [...document.getElementsByClassName('navbar-brand')];
  contentContainer = document.getElementById('main-content-container');
  stickyThreshold = navbar.offsetTop;
}, 0);