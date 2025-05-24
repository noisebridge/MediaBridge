describe('The Home Page', () => {
    it('successfully loads', () => {
      cy.visit('/')
    })
  })

describe('Movie Search using fixture', () => {

  beforeEach(() => {
    cy.intercept('GET', '/api/v1/movie/search*', { fixture: 'movies.json' }).as('movieSearch');
    cy.visit('/');
  });

  it('should display movies from fixture', () => {
    cy.get('input[name="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');
    cy.contains('Inception').should('exist');
  });

  it('should trigger the warning movie already added', () => {
    cy.get('input[name="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');
    cy.get('input[name="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');
    cy.contains('already added.').should('exist');
  });

  it('should delete movie after adding it', () => {
    cy.get('input[name="movie-search"]').type('Inception{enter}');
    cy.wait('@movieSearch');
    cy.contains('Inception').should('exist');

    cy.fixture('movies.json').then((movies) => {
      const inception = movies.find(movie => movie.title === 'Inception');
      cy.get(`button[name="remove-Inception"]`).click();
    });

    cy.contains('Inception').should('not.exist');
  });

  it('should select movie using autocomplete navigation', () => {
    cy.get('input[name="movie-search"]').type('Inc');
    cy.wait('@movieSearch');

    cy.get('input[name="movie-search"]').type('{downarrow}{downarrow}{enter}');

    cy.contains('The Shawshank Redemption').should('exist');
  });

  it('typing a title not found in the database, pressing the add movie button', () => {
    cy.get('input[name="movie-search"]').type('Shrek');
    cy.get('button[name="add-movie-button"]').click();
    cy.wait('@movieSearch');
    cy.contains('not found').should('exist');
  });

});