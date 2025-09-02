// Navigation handling
function showSection(sectionId, element) {
  // Hide all sections
  document.querySelectorAll('.section').forEach(section => {
    section.classList.remove('active');
  });
  
  // Remove active class from all nav links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
  });
  
  // Show selected section
  const section = document.getElementById(sectionId);
  if (section) {
    section.classList.add('active');
  } else {
    console.warn(`Section with id '${sectionId}' not found.`);
    return;
  }
  
  // Add active class to clicked nav link
  if (element) {
    element.classList.add('active');
  }
}