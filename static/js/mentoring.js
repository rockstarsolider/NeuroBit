// فیلتر منتورها
document.querySelectorAll('.filter-btn').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
  
      const filter = button.getAttribute('data-filter');
      const mentors = document.querySelectorAll('.mentor-card');
      let count = 0;
  
      mentors.forEach(mentor => {
        if (filter === 'all' || mentor.getAttribute('data-category').includes(filter)) {
          mentor.style.display = 'block';
          count++;
        } else {
          mentor.style.display = 'none';
        }
      });
  
      document.getElementById('mentorCount').textContent = count;
    });
});

document.querySelectorAll('.filter-btn')[0].click();
