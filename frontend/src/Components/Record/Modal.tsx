import React from 'react'
import { View, Pressable } from 'react-native'
import modalStyles from './modalStyles'
import { PropsWithChildren } from 'react'

type props = PropsWithChildren<{
    open: boolean
    close: () => void
}>

export default function Modal({ children, open, close }: props) {
    return (
        <Pressable style={open ? modalStyles.backdrop : modalStyles.invisible} onPress={close}>
            <View style={open ? modalStyles.modal : modalStyles.invisible} onStartShouldSetResponder={e => true} onTouchEnd={e => e.stopPropagation()}>
                {children}
            </View>
        </Pressable>
    )
}