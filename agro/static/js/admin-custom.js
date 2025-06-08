document.addEventListener('DOMContentLoaded', function() {
    // Add animation to form submissions
    $('form').on('submit', function() {
        $(this).find('button[type="submit"]').html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...'
        ).prop('disabled', true);
    });
    
    // Add tooltips everywhere
    $('[data-toggle="tooltip"]').tooltip();
    
    // Custom confirm dialogs
    $('.delete-link').on('click', function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = url;
            }
        });
    });
    
    // Add real-time notifications badge
    function updateNotificationBadge() {
        $.get('/get-notifications/', function(data) {
            const unreadCount = data.unread_count;
            if (unreadCount > 0) {
                $('.notification-badge').text(unreadCount).show();
            } else {
                $('.notification-badge').hide();
            }
        });
    }
    
    // Update every 60 seconds
    updateNotificationBadge();
    setInterval(updateNotificationBadge, 60000);
    
    // Add dashboard widgets
    if ($('#dashboard-page').length) {
        // Load stats via AJAX
        $.get('/admin-stats/', function(data) {
            $('#orders-widget .card-body').html(data.orders);
            $('#products-widget .card-body').html(data.products);
            $('#users-widget .card-body').html(data.users);
        });
    }
});