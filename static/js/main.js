// Main application JS for SAMPAH.AI

document.addEventListener("DOMContentLoaded", () => {
    // Sidebar toggle functionality
    const sidebar = document.getElementById("app-sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebarLabels = document.querySelectorAll(".sidebar-label");
    const sidebarLogo = document.getElementById("sidebar-logo-text");
    const sidebarStatus = document.getElementById("sidebar-status-container");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", () => {
            const isCollapsed = sidebar.classList.contains("w-14");
            
            if (isCollapsed) {
                // Expand sidebar
                sidebar.classList.remove("w-14");
                sidebar.classList.add("w-56");
                sidebarLabels.forEach(el => el.classList.remove("hidden"));
                if (sidebarLogo) sidebarLogo.classList.remove("hidden");
                if (sidebarStatus) sidebarStatus.classList.remove("justify-center");
                localStorage.setItem("sidebarCollapsed", "false");
            } else {
                // Collapse sidebar
                sidebar.classList.remove("w-56");
                sidebar.classList.add("w-14");
                sidebarLabels.forEach(el => el.classList.add("hidden"));
                if (sidebarLogo) sidebarLogo.classList.add("hidden");
                if (sidebarStatus) sidebarStatus.classList.add("justify-center");
                localStorage.setItem("sidebarCollapsed", "true");
            }
            // Notify other components (maps) that sidebar resized
            setTimeout(() => {
                document.dispatchEvent(new CustomEvent('sidebar:resized'));
            }, 300);
        });
    }

    // Notification drop-down functionality
    const notifBtn = document.getElementById("notif-btn");
    const notifDropdown = document.getElementById("notif-dropdown");

    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle("hidden");
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", () => {
            notifDropdown.classList.add("hidden");
        });

        notifDropdown.addEventListener("click", (e) => {
            e.stopPropagation(); // prevent closing when clicking inside
        });
    }

    // Flash message auto-fadeout
    const flashMessages = document.querySelectorAll(".flash-message");
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.classList.add("opacity-0", "transition-opacity", "duration-500");
            setTimeout(() => {
                msg.remove();
            }, 500);
        }, 4000); // Remove after 4 seconds
    });
});
