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

  # The book-sourced progressions wrap a real Wheel transposition. These
  # scenarios pin the cadences the publisher cares about — if any of the
  # 12 keys disagrees with the wheel, this feature fails.

  Scenario: The matriarchal cycle resolves to its own tonic in every key
    Given the baked progressions
    When I spin "matriarchal-cycle" to "D"
    Then the first step is rooted on "D"
    And the first step's mode is "Eólico"
    And the last step is rooted on "D"

  Scenario: The Frigio dominant lands a semitone above Eólico
    Given the baked progressions
    When I spin "matriarchal-cycle" to "A"
    Then step 3 is rooted on "E"
    And step 3's mode is "Frigio"

  Scenario: The major cadence ends a fifth above its dominant
    Given the baked progressions
    When I spin "jonico-cadence" to "G"
    Then step 1 is rooted on "G"
    And step 1's mode is "Jónico"
    And step 2 is rooted on "D"
    And step 2's mode is "Mixolidio"

  Scenario: The DodecaFuga walks all 12 stations without repetition
    Given the baked progressions
    When I spin "dodecafuga" to "A"
    Then the progression has 12 steps
    And every step has a unique mode
    And every step has a unique tonic

  Scenario: Every progression survives a spin to all 12 keys
    Given the baked progressions
    When I spin every progression to every key
    Then every step's scale is exactly seven or five notes
    And every step's scale has no repeated notes
