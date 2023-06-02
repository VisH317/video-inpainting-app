import React, { useState } from "react";
import { SafeAreaView, Text } from "react-native";
import {
  Gesture,
  GestureDetector,
  GestureHandlerRootView,
} from "react-native-gesture-handler";

export default function GestureDemo() {
  const [tGestureStart, setTGestureStart] = useState<undefined | string>();
  const [tGestureMove, setTGestureMove] = useState<undefined | string>();
  const [tGestureUpdate, setTGestureUpdate] = useState<undefined | string>();
  const [tGestureEnd, setTGestureEnd] = useState<undefined | string>();

  const pan = Gesture.Pan()
    .onStart((g) => {
      setTGestureStart(`${Math.round(g.x)}, ${Math.round(g.y)}`);
    })
    .onTouchesMove((g) => {
      setTGestureMove(
        `${Math.round(g.changedTouches[0].x)}, ${Math.round(
          g.changedTouches[0].y
        )}`
      );
    })
    .onUpdate((g) => {

      setTGestureUpdate(`${Math.round(g.x)}, ${Math.round(g.y)}`);
    })
    .onEnd((g) => {
      setTGestureEnd(`${Math.round(g.x)}, ${Math.round(g.y)}`);
    });
  return (
    <GestureHandlerRootView style={{ flex: 1, borderWidth: 2, borderColor: "blue" }}>
      <GestureDetector gesture={pan}>
        <SafeAreaView style={{ flex: 1, backgroundColor: "black", borderWidth: 2, borderColor: "blue" }}>
          <Text
            style={{ color: "white", fontSize: 24 }}
          >{`Gesture started at:  ${tGestureStart}`}</Text>
          <Text
            style={{ color: "white", fontSize: 24 }}
          >{`Gesture moved to:  ${tGestureMove}`}</Text>
          <Text
            style={{ color: "white", fontSize: 24 }}
          >{`Gesture updated to:  ${tGestureUpdate}`}</Text>
          <Text
            style={{ color: "white", fontSize: 24 }}
          >{`Gesture ended at:  ${tGestureEnd}`}</Text>
        </SafeAreaView>
      </GestureDetector>
    </GestureHandlerRootView>
  );
}