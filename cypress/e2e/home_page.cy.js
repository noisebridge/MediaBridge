describe('The Home Page', () => {
  it('successfully loads', () => {
    cy.visit('/');
  });
});

describe('Movie Search', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/v1/movie/search*', { fixture: 'movies.json' }).as('movieSearch');
    cy.visit('/');
  });

  it('displays movie', () => {
    cy.get('input[id="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');

    cy.get('[id="movie-card"]').should('have.length.at.least', 1);
    cy.get('[id="movie-card"]').first().contains('Inception');
  });

  it('triggers the warning movie already added', () => {
    cy.get('input[id="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');

    cy.get('input[id="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');

    cy.get('[id="movie-warning"]').should('contain', 'already added');
  });

  it('deletes movie after adding it', () => {
    cy.get('input[id="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');

    cy.get('[id="movie-card"]').should('exist');

    cy.contains('[id="movie-card"]', 'Inception')
      .find('button[id="remove-movie"]')
      .click();

    cy.contains('Inception').should('not.exist');
});

  it('selects movie using autocomplete navigation', () => {
    cy.get('input[id="movie-search"]').type('Inc');
    cy.wait('@movieSearch');

    cy.get('input[id="movie-search"]').type('{downarrow}{downarrow}{enter}');

    cy.contains('The Shawshank Redemption').should('exist');
  });

  it('typing a title not found in the database, pressing the add movie button', () => {
    cy.get('input[id="movie-search"]').type('Shrek');
    cy.get('button[id="add-movie-button"]').click();
    cy.wait('@movieSearch');

    cy.get('[id="movie-warning"]').should('contain', 'not found');
  });
});