// ===== Mobile menu toggle =====
const mobileMenuButton = document.getElementById("mobile-menu-button");
const mobileMenu = document.getElementById("mobile-menu");

if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
    });
}

// ===== File upload preview =====
const fileInput = document.getElementById("file-upload");
const fileNameSpan = document.getElementById("file-name");
const fileAttachedIcon = document.getElementById("file-attached-icon");

if (fileInput) {
    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            fileNameSpan.textContent = file.name;
            fileNameSpan.classList.remove("hidden");
            fileAttachedIcon.classList.remove("hidden");
        } else {
            fileNameSpan.classList.add("hidden");
            fileAttachedIcon.classList.add("hidden");
        }
    });
}

// ===== Forum filter buttons (optional) =====
const filterButtons = document.querySelectorAll(".forum-filter-btn");
filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        filterButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        const filter = btn.textContent.toLowerCase();

        // Loop through posts and show/hide based on filter
        const posts = document.querySelectorAll(".space-y-4 > div");
        posts.forEach(post => {
            if (filter === "all" || post.textContent.toLowerCase().includes(filter)) {
                post.style.display = "";
            } else {
                post.style.display = "none";
            }
        });
    });
});
