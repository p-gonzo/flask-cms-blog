var momentRelativeTime = function(utcString) {
    return moment.utc(utcString).fromNow();
}