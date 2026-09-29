import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../theme/theme';

export const ErrorMessage = ({ message }: { message: string }) => (
    <View style={styles.container}>
        <Text style={styles.text}>{message}</Text>
    </View>
);

const styles = StyleSheet.create({
    container: {
        padding: theme.spacing.m,
        backgroundColor: '#FFEBEB',
        borderRadius: theme.borderRadius.m,
        marginVertical: theme.spacing.s,
    },
    text: {
        ...theme.typography.body,
        color: theme.colors.error,
        textAlign: 'center',
    }
});
