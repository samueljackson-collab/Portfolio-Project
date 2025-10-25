describe('Portfolio smoke test', () => {
  it('loads the homepage', () => {
    cy.visit('/');
    cy.contains('Portfolio Showcase');
  });
});
