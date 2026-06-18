Feature: Learning the Dodecamundo
  As a music student new to the Sistema Fractal
  I want to explore the 12 note-worlds as colored, glyphed cards
  So that notes stop being black/white keys and become worlds with meaning

  Background:
    Given a fresh Dodecamundo

  Scenario: The system begins from La (A), not Do (C)
    When I look at the first world
    Then its note is "A"
    And its mode is "Eólico"

  Scenario: Twelve worlds split into five stars and seven naturals
    When I count the worlds
    Then there are 12 worlds in total
    And 5 of them are pentatonic stars
    And 7 of them are natural notes

  Scenario: A natural note shows its Greek mode glyph
    When I draw the carta for "C"
    Then the carta shows the glyph "□"
    And the carta names the mode "Jónico"

  Scenario: A black key is a pentatonic star with a roman numeral
    When I draw the carta for "F#"
    Then the carta shows the glyph "★"
    And the carta shows the roman numeral "III"
