Feature: Composing with the Gátople
  As a learner playing with the Fractal System
  I want to use the pentatonic-first method and the clock
  So that I can find scales and chords organically, without fear of math

  Scenario: Cero Pitágoras — five fingers on the five black keys
    Given a fresh Dodecamundo
    When I perform Cero Pitágoras from "A"
    Then I get a 5-note pentatonic seed
    And the seed has no semitone steps

  Scenario: Every pentatonic mode avoids semitones
    Given a fresh Dodecamundo
    When I build all five pentatonic modes on "A"
    Then none of them contains a semitone step

  Scenario: The pentatonic universe has sixty microstructures
    Given a fresh Dodecamundo
    When I generate every pentatonic microstructure
    Then there are 60 microstructures

  Scenario: Measuring the distance between two worlds as an angle
    Given a fresh Dodecamundo
    When I measure the angle from "A" to "C"
    Then the angle is 90 degrees

  Scenario: Writing a chord in Fractal symbols
    Given a fresh Dodecamundo
    When I spell the chord "A C E"
    Then it reads "⋮ □ ♀" in glyphs
